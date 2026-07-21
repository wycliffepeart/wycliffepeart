"""GitHub issue, branch, PR, and Project publishing automation."""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Callable, Optional, TextIO

from scripts.codex_json import CodexJsonError
from scripts.env_utils import env_int, load_environment_file
from scripts.logging_utils import summarize_args, write_value
from scripts.posts import (
    PENDING_STATUS,
    POST_INDEX_PATH,
    PULL_REQUEST_STATUS,
    indexed_posts_with_status,
    load_post_metadata,
    load_posts_index,
    update_indexed_post_status,
)

LOGGER = logging.getLogger(__name__)

GITHUB_TOKEN_ENV = "GH_TOKEN"
GITHUB_REPO_ENV = "WP_GITHUB_REPO"
GITHUB_PROJECT_ID_ENV = "WP_GITHUB_PROJECT_ID"
GITHUB_PROJECT_OWNER_ENV = "WP_GITHUB_PROJECT_OWNER"


def add_github_publish_options(parser: argparse.ArgumentParser, *, include_markdown: bool) -> None:
    if include_markdown:
        parser.add_argument("markdown", help="LinkedIn post Markdown file to publish")
    parser.add_argument(
        "--repo",
        help="GitHub repository in OWNER/REPO format. If omitted, gh infers the repository.",
    )
    parser.add_argument("--base", default="main", help="base branch for the pull request")
    if include_markdown:
        parser.add_argument("--branch", help="branch to create. Defaults to feat/publish-<slug>.")
    parser.add_argument("--git-bin", default="git", help="git executable to run")
    parser.add_argument("--gh-bin", default="gh", help="GitHub CLI executable to run")
    parser.add_argument(
        "--env-file",
        default=".env.local",
        help="dotenv file to load before reading GitHub environment variables",
    )
    parser.add_argument(
        "--github-token-env",
        default=GITHUB_TOKEN_ENV,
        help="environment variable containing the fine-grained GitHub token",
    )
    parser.add_argument(
        "--label",
        action="append",
        dest="labels",
        help="issue label to apply. May be repeated. Defaults to content and linkedin.",
    )
    parser.add_argument("--issue-title", help="override the generated issue title")
    parser.add_argument("--pr-title", help="override the generated pull request title")
    parser.add_argument("--commit-message", help="override the generated commit message")
    parser.add_argument("--project-id", type=int, help="GitHub Project number/id to add the issue to")
    parser.add_argument(
        "--project-owner",
        help="GitHub user or org that owns the project. Defaults to the owner from --repo.",
    )
    parser.add_argument(
        "--status",
        default=PENDING_STATUS,
        help=f"post status to publish from {POST_INDEX_PATH}. Defaults to {PENDING_STATUS}.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print planned git and gh commands without creating anything",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )


def repo_arg(repo: Optional[str]) -> list[str]:
    return ["--repo", repo] if repo else []


def infer_owner_from_repo(repo: Optional[str]) -> Optional[str]:
    if not repo:
        return None

    parts = repo.split("/")
    if len(parts) == 2:
        return parts[0]
    if len(parts) == 3:
        return parts[1]
    return None


def require_github_token(token_env: str) -> dict:
    token = os.environ.get(token_env)
    if not token:
        LOGGER.error("GitHub token environment variable is missing: env=%s", token_env)
        raise CodexJsonError(
            f"Set {token_env} to a fine-grained GitHub token before running this command."
        )

    env = os.environ.copy()
    env["GH_TOKEN"] = token
    LOGGER.info("Prepared GitHub CLI environment from token env: sourceEnv=%s targetEnv=GH_TOKEN", token_env)
    return env


def run_external_command(
    command: list[str],
    *,
    dry_run: bool,
    env: Optional[dict] = None,
    env_names: Optional[list[str]] = None,
) -> dict:
    LOGGER.info("Preparing external command: dryRun=%s command=%s", dry_run, command)
    if dry_run:
        output = {"command": command}
        if env_names:
            output["env"] = env_names
        return output

    completed = subprocess.run(command, check=False, capture_output=True, text=True, env=env)
    LOGGER.info(
        "External command completed: returncode=%s stdoutChars=%s stderrChars=%s command=%s",
        completed.returncode,
        len(completed.stdout),
        len(completed.stderr),
        command,
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or f"Command failed: {command[0]}"
        LOGGER.error("External command failed: command=%s message=%s", command, message)
        raise CodexJsonError(message)

    return {"command": command, "stdout": completed.stdout.strip()}


def is_existing_branch_error(message: str) -> bool:
    return "a branch named" in message and "already exists" in message


def run_create_or_recreate_branch(args: argparse.Namespace, branch: str) -> dict:
    create_command = [args.git_bin, "switch", "-c", branch, args.base]
    if args.dry_run:
        return run_external_command(create_command, dry_run=True)

    try:
        return run_external_command(create_command, dry_run=False)
    except CodexJsonError as exc:
        if not is_existing_branch_error(str(exc)):
            raise

        base_switch_command = [args.git_bin, "switch", args.base]
        delete_command = [args.git_bin, "branch", "-D", branch]
        LOGGER.info(
            "Branch already exists; deleting and recreating branch: branch=%s baseCommand=%s deleteCommand=%s createCommand=%s",
            branch,
            base_switch_command,
            delete_command,
            create_command,
        )
        base_switch_step = run_external_command(base_switch_command, dry_run=False)
        delete_step = run_external_command(delete_command, dry_run=False)
        recreate_step = run_external_command(create_command, dry_run=False)
        return {
            "command": create_command,
            "baseSwitchCommand": base_switch_command,
            "baseSwitchStdout": base_switch_step["stdout"],
            "deleteCommand": delete_command,
            "deleteStdout": delete_step["stdout"],
            "stdout": recreate_step["stdout"],
            "recreatedExistingBranch": True,
        }


def issue_number_from_url(issue_url: str) -> str:
    match = re.search(r"/issues/(\d+)\s*$", issue_url)
    if not match:
        LOGGER.error("Could not parse issue number from URL: url=%s", issue_url)
        raise CodexJsonError(f"Could not parse issue number from URL: {issue_url}")
    return match.group(1)


def placeholder_issue_url(repo: Optional[str]) -> str:
    owner_repo = repo or "OWNER/REPO"
    return f"https://github.com/{owner_repo}/issues/<issue-number>"


def github_issue_title(args: argparse.Namespace, metadata: dict) -> str:
    return args.issue_title or f"Publish LinkedIn draft: {metadata['title']}"


def github_issue_create_command(args: argparse.Namespace, metadata: dict) -> list[str]:
    command = [
        args.gh_bin,
        "issue",
        "create",
        *repo_arg(args.repo),
        "--title",
        github_issue_title(args, metadata),
        "--body-file",
        args.markdown,
    ]
    for label in args.labels or ["content", "linkedin"]:
        command.extend(["--label", label])
    return command


def github_repo_view_command(args: argparse.Namespace) -> list[str]:
    command = [args.gh_bin, "repo", "view"]
    if args.repo:
        command.append(args.repo)
    command.extend(["--json", "nameWithOwner,viewerPermission"])
    return command


def github_issue_list_by_title_command(args: argparse.Namespace, title: str) -> list[str]:
    return [
        args.gh_bin,
        "issue",
        "list",
        *repo_arg(args.repo),
        "--state",
        "open",
        "--search",
        f'in:title "{title}"',
        "--json",
        "title,url",
        "--limit",
        "20",
    ]


def github_repository_access_error(repo: Optional[str], token_env: str, message: str) -> str:
    target = repo or "the current repository"
    return (
        f"GitHub token from {token_env} cannot access {target}. "
        "Confirm the token is active, is authorized for any required organization SSO, "
        "and has access to this repository with Issues, Pull requests, and Contents permissions. "
        f"GitHub CLI error: {message}"
    )


def verify_github_repository_access(args: argparse.Namespace, github_env: Optional[dict]) -> None:
    if args.dry_run:
        return

    try:
        run_external_command(
            github_repo_view_command(args),
            dry_run=False,
            env=github_env,
        )
    except CodexJsonError as exc:
        LOGGER.error("GitHub repository access check failed: repo=%s", args.repo or "<inferred>")
        raise CodexJsonError(
            github_repository_access_error(args.repo, args.github_token_env, str(exc))
        ) from exc


def resolve_project_reference(args: argparse.Namespace, repo: Optional[str]) -> Optional[tuple[str, int]]:
    project_id = args.project_id if args.project_id is not None else env_int(GITHUB_PROJECT_ID_ENV)
    project_owner = args.project_owner or os.environ.get(GITHUB_PROJECT_OWNER_ENV) or infer_owner_from_repo(repo)

    if project_id is None:
        if args.project_owner is not None or os.environ.get(GITHUB_PROJECT_OWNER_ENV):
            raise CodexJsonError("--project-owner requires --project-id or WP_GITHUB_PROJECT_ID.")
        return None

    if not project_owner:
        raise CodexJsonError("--project-id requires --repo OWNER/REPO or --project-owner.")

    return project_owner, project_id


def github_project_item_add_command(args: argparse.Namespace, issue_url: str, repo: Optional[str]) -> Optional[list[str]]:
    project = resolve_project_reference(args, repo)
    if project is None:
        return None

    project_owner, project_id = project
    return [
        args.gh_bin,
        "project",
        "item-add",
        str(project_id),
        "--owner",
        project_owner,
        "--url",
        issue_url,
    ]


def github_pr_create_command(args: argparse.Namespace, metadata: dict, branch: str, issue_number: str) -> list[str]:
    body = (
        f"Closes #{issue_number}\n\n"
        f"Adds the LinkedIn draft: {metadata['title']}."
    )
    return [
        args.gh_bin,
        "pr",
        "create",
        *repo_arg(args.repo),
        "--base",
        args.base,
        "--head",
        branch,
        "--title",
        args.pr_title or f"Add LinkedIn post: {metadata['title']}",
        "--body",
        body,
    ]


def find_existing_issue_by_title(
    args: argparse.Namespace,
    title: str,
    *,
    github_env: Optional[dict],
    gh_env_names: list[str],
) -> tuple[dict, Optional[str]]:
    step = run_external_command(
        github_issue_list_by_title_command(args, title),
        dry_run=args.dry_run,
        env=github_env,
        env_names=gh_env_names,
    )
    try:
        issues = json.loads(step["stdout"] or "[]")
    except json.JSONDecodeError as exc:
        raise CodexJsonError("Could not parse GitHub issue list output as JSON.") from exc

    if not isinstance(issues, list):
        raise CodexJsonError("GitHub issue list output must be a JSON array.")

    for issue in issues:
        if (
            isinstance(issue, dict)
            and issue.get("title") == title
            and isinstance(issue.get("url"), str)
            and issue["url"].strip()
        ):
            step["matched"] = True
            return step, issue["url"]

    step["matched"] = False
    return step, None


def publish_github_post(
    args: argparse.Namespace,
    metadata: dict,
    *,
    github_env: Optional[dict],
    gh_env_names: list[str],
    status_update: Optional[Callable[[], dict]] = None,
) -> dict:
    LOGGER.info("Starting GitHub post publish flow: args=%s metadata=%s", summarize_args(args), metadata)
    branch = getattr(args, "branch", None) or f"feat/publish-{metadata['slug']}"
    commit_message = args.commit_message or f"Add LinkedIn post: {metadata['slug']}"

    LOGGER.info(
        "Prepared GitHub post publish flow: markdown=%s branch=%s base=%s dryRun=%s",
        args.markdown,
        branch,
        args.base,
        args.dry_run,
    )

    steps = []
    branch_step = run_create_or_recreate_branch(args, branch)
    steps.append({"name": "create_branch", **branch_step})

    issue_title = github_issue_title(args, metadata)
    issue_step = run_external_command(
        github_issue_create_command(args, metadata),
        dry_run=args.dry_run,
        env=github_env,
        env_names=gh_env_names,
    )
    issue_url = placeholder_issue_url(args.repo) if args.dry_run else issue_step["stdout"].splitlines()[-1]
    steps.append({"name": "create_issue", **issue_step})
    issue_number = "<issue-number>" if args.dry_run else issue_number_from_url(issue_url)

    project_command = github_project_item_add_command(args, issue_url, args.repo)
    if project_command:
        steps.append(
            {
                "name": "add_issue_to_project",
                **run_external_command(
                    project_command,
                    dry_run=args.dry_run,
                    env=github_env,
                    env_names=gh_env_names,
                ),
            }
        )

    git_steps = [
        ("stage_post", [args.git_bin, "add", args.markdown, str(POST_INDEX_PATH)]),
        ("commit_post", [args.git_bin, "commit", "-m", commit_message]),
        ("push_branch", [args.git_bin, "push", "-u", "origin", branch]),
    ]
    for name, command in git_steps:
        steps.append({"name": name, **run_external_command(command, dry_run=args.dry_run)})

    pr_step = run_external_command(
        github_pr_create_command(args, metadata, branch, issue_number),
        dry_run=args.dry_run,
        env=github_env,
        env_names=gh_env_names,
    )
    pr_url = f"https://github.com/{args.repo or 'OWNER/REPO'}/pull/<pr-number>" if args.dry_run else pr_step["stdout"].splitlines()[-1]
    steps.append({"name": "create_pull_request", **pr_step})

    if status_update:
        steps.append({"name": "update_post_status", **status_update()})
        status_commit_message = f"Mark LinkedIn post as PR: {metadata['slug']}"
        status_git_steps = [
            ("stage_status", [args.git_bin, "add", args.markdown, str(POST_INDEX_PATH)]),
            ("commit_status", [args.git_bin, "commit", "-m", status_commit_message]),
            ("push_status", [args.git_bin, "push", "origin", branch]),
        ]
        for name, command in status_git_steps:
            steps.append({"name": name, **run_external_command(command, dry_run=args.dry_run)})

    output = {
        "dryRun": args.dry_run,
        "post": {
            "title": metadata["title"],
            "slug": metadata["slug"],
            "markdown": args.markdown,
        },
        "branch": branch,
        "issueUrl": issue_url,
        "pullRequestUrl": pr_url,
        "steps": steps,
    }
    LOGGER.info("GitHub post publish flow completed: branch=%s issueUrl=%s prUrl=%s", branch, issue_url, pr_url)
    return output


def run_github_publish_post(args: argparse.Namespace, *, stdout: TextIO) -> int:
    LOGGER.info("Starting GitHub publish-post flow: args=%s", summarize_args(args))
    load_environment_file(args.env_file)
    args.repo = args.repo or os.environ.get(GITHUB_REPO_ENV)

    metadata = load_post_metadata(Path(args.markdown))
    github_env = None if args.dry_run else require_github_token(args.github_token_env)
    verify_github_repository_access(args, github_env)
    output = publish_github_post(
        args,
        metadata,
        github_env=github_env,
        gh_env_names=["GH_TOKEN"],
    )
    write_value(output, pretty=args.pretty, stdout=stdout)
    LOGGER.info(
        "GitHub publish-post flow completed: branch=%s issueUrl=%s prUrl=%s",
        output["branch"],
        output["issueUrl"],
        output["pullRequestUrl"],
    )
    return 0


def run_publish_github(args: argparse.Namespace, *, stdout: TextIO) -> int:
    LOGGER.info("Starting publish github flow: args=%s", summarize_args(args))
    load_environment_file(args.env_file)
    args.repo = args.repo or os.environ.get(GITHUB_REPO_ENV)

    root = Path.cwd()
    index = load_posts_index(root / POST_INDEX_PATH)
    pending_posts = indexed_posts_with_status(index, args.status)
    github_env = None if args.dry_run or not pending_posts else require_github_token(args.github_token_env)
    if pending_posts:
        verify_github_repository_access(args, github_env)
    outputs = []

    for post in pending_posts:
        markdown = post.get("markdown")
        post_id = post.get("id")
        if not isinstance(markdown, str) or not markdown.strip():
            raise CodexJsonError("Pending post is missing a markdown path.")
        if not isinstance(post_id, str) or not post_id.strip():
            raise CodexJsonError(f"Pending post is missing an id: {markdown}")

        child_args = argparse.Namespace(**vars(args))
        child_args.markdown = markdown
        child_args.branch = None
        metadata = load_post_metadata(root / markdown)
        outputs.append(
            publish_github_post(
                child_args,
                metadata,
                github_env=github_env,
                gh_env_names=["GH_TOKEN"],
                status_update=lambda post_id=post_id, markdown=markdown: update_indexed_post_status(
                    root=root,
                    post_id=post_id,
                    markdown=markdown,
                    status=PULL_REQUEST_STATUS,
                    dry_run=args.dry_run,
                ),
            )
        )

    output = {
        "dryRun": args.dry_run,
        "fromStatus": args.status,
        "toStatus": PULL_REQUEST_STATUS,
        "postCount": len(outputs),
        "posts": outputs,
    }
    write_value(output, pretty=args.pretty, stdout=stdout)
    LOGGER.info("Publish github flow completed: postCount=%s", len(outputs))
    return 0
