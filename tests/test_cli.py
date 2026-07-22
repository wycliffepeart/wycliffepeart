import io
import json
import logging
import os
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.cli import (
    SpringBootFormatter,
    build_codex_prompt,
    load_post_metadata,
    persist_post_response,
    post_index_entry,
    run_linkedin_carousel_generate,
    run_github_publish_post,
    run_publish_github,
    run_codex_json,
    run_codex_e,
    validate_post_response,
)
from scripts.codex_json import CodexJsonError


class Args:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class CliTests(unittest.TestCase):
    def post_response(self):
        return {
            "id": "73980542-7a40-4811-8494-14b3984b7f5b",
            "title": "Focused Reviews Catch Risk Earlier",
            "slug": "focused-reviews-catch-risk-earlier",
            "createdAt": "2026-07-21T02:03:04Z",
            "date": "2026-07-21",
            "topic": "Software quality",
            "excerpt": "Focused code reviews catch risk earlier by matching reviewer attention to the parts of a change most likely to fail.",
            "tags": [
                "software-quality",
                "code-review",
                "developer-productivity",
            ],
            "status": "draft",
            "markdown": (
                "workspace/blog/linkedin/posts/2026/07/"
                "2026-07-21-020304-focused-reviews-catch-risk-earlier.md"
            ),
            "body": "Good reviews start with the risk in the change.\n\n#SoftwareQuality #CodeReview",
        }

    def write_post_markdown(self, root: Path, *, status: str = "draft") -> Path:
        post_path = root / "workspace/blog/linkedin/posts/2026/07/2026-07-21-020304-focused-reviews-catch-risk-earlier.md"
        post_path.parent.mkdir(parents=True)
        post_path.write_text(
            f"""---
id: "73980542-7a40-4811-8494-14b3984b7f5b"
title: "Focused Reviews Catch Risk Earlier"
slug: "focused-reviews-catch-risk-earlier"
createdAt: "2026-07-21T02:03:04Z"
topic: "Software quality"
status: "{status}"
tags:
  - "software-quality"
  - "code-review"
---

# Focused Reviews Catch Risk Earlier

Good reviews start with the risk in the change.
""",
            encoding="utf-8",
        )
        return post_path

    def publish_args(self, post_path: Path, **overrides):
        values = {
            "markdown": str(post_path),
            "repo": "9to5guru/wp-workflow",
            "base": "main",
            "branch": None,
            "git_bin": "git",
            "gh_bin": "gh",
            "env_file": ".env.local",
            "github_token_env": "GH_FINE_GRAINED_TOKEN",
            "labels": None,
            "issue_title": None,
            "pr_title": None,
            "commit_message": None,
            "project_id": 1,
            "project_owner": None,
            "dry_run": True,
            "pretty": False,
        }
        values.update(overrides)
        return Args(**values)

    def publish_github_args(self, **overrides):
        values = {
            "repo": "9to5guru/wp-workflow",
            "base": "main",
            "git_bin": "git",
            "gh_bin": "gh",
            "env_file": ".env.local",
            "github_token_env": "GH_FINE_GRAINED_TOKEN",
            "labels": None,
            "issue_title": None,
            "pr_title": None,
            "commit_message": None,
            "project_id": 1,
            "project_owner": None,
            "status": "pending",
            "dry_run": True,
            "pretty": False,
        }
        values.update(overrides)
        return Args(**values)

    def write_posts_index(self, root: Path, posts: list[dict]) -> Path:
        index_path = root / "workspace/blog/linkedin/posts.json"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(
            json.dumps({"version": 1, "updatedAt": "2026-07-21T02:03:04Z", "posts": posts}),
            encoding="utf-8",
        )
        return index_path

    def test_codex_prompt_requires_metadata_json(self):
        prompt = build_codex_prompt("write linkedin post about idempotency, respond in json")

        self.assertIn("Respond only with a valid JSON object.", prompt)
        self.assertIn("- markdown: string, a path under workspace/blog/linkedin/posts/YYYY/MM/", prompt)
        self.assertIn("- body: string, the complete LinkedIn post body", prompt)
        self.assertIn("- status: string, use pending for new generated posts.", prompt)
        self.assertNotIn('"id": "fcb42734-4061-4c59-9ba4-1dac78106270"', prompt)

    def test_codex_json_field_output_stays_json(self):
        stdout = io.StringIO()
        args = Args(path="-", field="post", first=False, pretty=False)

        run_codex_json(args, stdin=io.StringIO('codex\n{"post": "hello"}'), stdout=stdout)

        self.assertEqual(json.loads(stdout.getvalue()), "hello")

    def test_validate_post_response_rejects_missing_schema_fields(self):
        with self.assertLogs("scripts.posts", level="ERROR") as logs:
            with self.assertRaises(CodexJsonError):
                validate_post_response({"post": "hello"})

        self.assertIn("missing required fields", "\n".join(logs.output))

    def test_persist_post_response_writes_markdown_and_updates_index(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            index_path = root / "workspace/blog/linkedin/posts.json"
            index_path.parent.mkdir(parents=True)
            index_path.write_text(
                json.dumps({"version": 1, "updatedAt": "2026-07-21T01:00:00Z", "posts": []}),
                encoding="utf-8",
            )

            with self.assertLogs("scripts.posts", level="INFO") as logs:
                entry = persist_post_response(self.post_response(), root=root)

            markdown_path = root / entry["markdown"]
            self.assertTrue(markdown_path.exists())
            self.assertEqual(entry["status"], "pending")
            self.assertNotIn("updatedAt", entry)
            self.assertNotIn("body", entry)
            self.assertIn("Starting post persistence flow", "\n".join(logs.output))
            self.assertIn("Writing posts index file", "\n".join(logs.output))
            self.assertIn("Post persistence flow completed", "\n".join(logs.output))

            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn('id: "73980542-7a40-4811-8494-14b3984b7f5b"', markdown)
            self.assertIn('status: "pending"', markdown)
            self.assertIn("# Focused Reviews Catch Risk Earlier", markdown)
            self.assertIn("Good reviews start with the risk in the change.", markdown)

            index = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(index["updatedAt"], "2026-07-21T02:03:04Z")
            self.assertEqual(index["posts"], [entry])

    def test_codex_e_outputs_pending_status_for_generated_post(self):
        stdout = io.StringIO()
        args = Args(
            prompt="write linkedin post random post",
            codex_bin="codex",
            pretty=False,
            dry_run=False,
            no_write=True,
            env_file=None,
            retries=None,
        )

        with patch("scripts.posts.subprocess.run") as run:
            run.return_value = Args(
                returncode=0,
                stdout=json.dumps(self.post_response()),
                stderr="",
            )

            run_codex_e(args, stdout=stdout)

        output = json.loads(stdout.getvalue())
        self.assertEqual(output["status"], "pending")

    def test_codex_e_retries_duplicate_slug_until_generated_post_persists(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            duplicate_response = self.post_response()
            existing_entry = post_index_entry(duplicate_response)
            existing_entry["id"] = "7a87ef2b-c639-4c37-a783-b48b7b5f0a86"
            existing_entry["markdown"] = (
                "workspace/blog/linkedin/posts/2026/07/"
                "2026-07-21-015959-focused-reviews-catch-risk-earlier.md"
            )
            index_path = self.write_posts_index(root, [existing_entry])

            regenerated_response = self.post_response()
            regenerated_response.update(
                {
                    "id": "d5df8e6f-875c-488b-84ee-86f19a4faf13",
                    "title": "Useful Defaults Make Automation Easier",
                    "slug": "useful-defaults-make-automation-easier",
                    "createdAt": "2026-07-21T02:04:05Z",
                    "date": "2026-07-21",
                    "topic": "Workflow automation",
                    "excerpt": "Useful defaults make automation easier by reducing repeat decisions while preserving room for human judgment.",
                    "tags": ["workflow-automation", "developer-productivity", "systems-thinking"],
                    "markdown": (
                        "workspace/blog/linkedin/posts/2026/07/"
                        "2026-07-21-020405-useful-defaults-make-automation-easier.md"
                    ),
                    "body": "Useful defaults make automation easier.\n\n#WorkflowAutomation",
                }
            )
            stdout = io.StringIO()
            args = Args(
                prompt="write linkedin post random post",
                codex_bin="codex",
                pretty=False,
                dry_run=False,
                no_write=False,
                env_file=None,
                retries=5,
            )

            def completed(response):
                return Args(returncode=0, stdout=json.dumps(response), stderr="")

            previous_cwd = os.getcwd()
            try:
                os.chdir(root)
                with patch("scripts.posts.subprocess.run") as run:
                    run.side_effect = [
                        completed(duplicate_response),
                        completed(regenerated_response),
                    ]

                    run_codex_e(args, stdout=stdout)

                index = json.loads(index_path.read_text(encoding="utf-8"))
            finally:
                os.chdir(previous_cwd)

        output = json.loads(stdout.getvalue())
        self.assertEqual(output["slug"], "useful-defaults-make-automation-easier")
        self.assertEqual(run.call_count, 2)
        self.assertIn("Post slug already exists", run.call_args_list[1].args[0][2])
        self.assertEqual(len(index["posts"]), 2)
        self.assertEqual(index["posts"][1]["slug"], "useful-defaults-make-automation-easier")

    def test_codex_e_retries_invalid_uuid_until_generated_post_validates(self):
        stdout = io.StringIO()
        invalid_response = self.post_response()
        invalid_response["id"] = "c2c71892-3a1f-4d1f-b7f8-2f6f2ec9d4a"
        valid_response = self.post_response()
        args = Args(
            prompt="write linkedin post random post",
            codex_bin="codex",
            pretty=False,
            dry_run=False,
            no_write=True,
            env_file=None,
            retries=5,
        )

        def completed(response):
            return Args(returncode=0, stdout=json.dumps(response), stderr="")

        with patch("scripts.posts.subprocess.run") as run:
            run.side_effect = [
                completed(invalid_response),
                completed(valid_response),
            ]

            run_codex_e(args, stdout=stdout)

        output = json.loads(stdout.getvalue())
        self.assertEqual(output["id"], "73980542-7a40-4811-8494-14b3984b7f5b")
        self.assertEqual(run.call_count, 2)
        self.assertIn("Codex response field 'id' must be a UUID v4 string.", run.call_args_list[1].args[0][2])

    def test_persist_post_response_rejects_duplicate_slug(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            response = self.post_response()
            index_path = root / "workspace/blog/linkedin/posts.json"
            index_path.parent.mkdir(parents=True)
            index_path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "updatedAt": response["createdAt"],
                        "posts": [post_index_entry(response)],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertLogs("scripts.posts", level="ERROR") as logs:
                with self.assertRaises(CodexJsonError):
                    persist_post_response(response, root=root)

            self.assertIn("Duplicate post id detected", "\n".join(logs.output))

    def test_spring_boot_formatter_shape(self):
        record = logging.LogRecord(
            "cli",
            logging.INFO,
            __file__,
            1,
            "hello %s",
            ("world",),
            None,
        )
        record.created = 1780000000.123
        record.msecs = 123
        record.process = 12345
        record.threadName = "MainThread"

        line = SpringBootFormatter().format(record)

        self.assertRegex(
            line,
            re.compile(
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}[+-]\d{4}"
                r"\s+INFO 12345 --- \[\s+MainThread\] cli\s+: hello world$"
            ),
        )

    def test_load_post_metadata_reads_front_matter(self):
        with tempfile.TemporaryDirectory() as workspace:
            post_path = self.write_post_markdown(Path(workspace))

            metadata = load_post_metadata(post_path)

        self.assertEqual(metadata["title"], "Focused Reviews Catch Risk Earlier")
        self.assertEqual(metadata["slug"], "focused-reviews-catch-risk-earlier")
        self.assertEqual(metadata["status"], "draft")

    def test_github_publish_post_dry_run_uses_fine_grained_token_env_name(self):
        with tempfile.TemporaryDirectory() as workspace:
            post_path = self.write_post_markdown(Path(workspace))
            stdout = io.StringIO()

            run_github_publish_post(self.publish_args(post_path), stdout=stdout)

        output = json.loads(stdout.getvalue())
        self.assertTrue(output["dryRun"])
        self.assertEqual(output["branch"], "feat/publish-focused-reviews-catch-risk-earlier")
        self.assertEqual(output["issueUrl"], "https://github.com/9to5guru/wp-workflow/issues/<issue-number>")
        self.assertEqual(
            [step["name"] for step in output["steps"]],
            [
                "create_branch",
                "create_issue",
                "add_issue_to_project",
                "stage_post",
                "commit_post",
                "push_branch",
                "create_pull_request",
            ],
        )
        issue_step = next(step for step in output["steps"] if step["name"] == "create_issue")
        self.assertEqual(issue_step["env"], ["GH_TOKEN"])
        self.assertNotIn("GH_FINE_GRAINED_TOKEN", json.dumps(output))
        self.assertTrue(any("Closes #<issue-number>" in value for value in output["steps"][-1]["command"]))

    def test_github_publish_post_accepts_project_id(self):
        with tempfile.TemporaryDirectory() as workspace:
            post_path = self.write_post_markdown(Path(workspace))
            stdout = io.StringIO()
            args = self.publish_args(
                post_path,
                project_id=5,
            )

            run_github_publish_post(args, stdout=stdout)

        output = json.loads(stdout.getvalue())
        project_step = next(step for step in output["steps"] if step["name"] == "add_issue_to_project")
        self.assertEqual(
            project_step["command"],
            [
                "gh",
                "project",
                "item-add",
                "5",
                "--owner",
                "9to5guru",
                "--url",
                "https://github.com/9to5guru/wp-workflow/issues/<issue-number>",
            ],
        )

    def test_github_publish_post_loads_dotenv_defaults(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            post_path = self.write_post_markdown(root)
            env_file = root / ".env.local"
            env_file.write_text(
                "\n".join(
                    [
                        "GH_FINE_GRAINED_TOKEN=secret-token",
                        "WP_GITHUB_REPO=9to5guru/wp-workflow",
                        "WP_GITHUB_PROJECT_ID=5",
                    ]
                ),
                encoding="utf-8",
            )
            stdout = io.StringIO()
            args = self.publish_args(
                post_path,
                repo=None,
                env_file=str(env_file),
                project_id=None,
                project_owner=None,
                dry_run=False,
            )

            def completed(stdout_text):
                return Args(returncode=0, stdout=stdout_text, stderr="")

            with patch.dict("os.environ", {}, clear=True):
                with patch("scripts.github_publish.subprocess.run") as run:
                    run.side_effect = [
                        completed('{"nameWithOwner":"9to5guru/wp-workflow","viewerPermission":"WRITE"}\n'),
                        completed(""),
                        completed("https://github.com/9to5guru/wp-workflow/issues/123\n"),
                        completed('{"id":"project-item"}\n'),
                        completed(""),
                        completed(""),
                        completed(""),
                        completed("https://github.com/9to5guru/wp-workflow/pull/456\n"),
                    ]

                    run_github_publish_post(args, stdout=stdout)

        output = json.loads(stdout.getvalue())
        project_step = next(step for step in output["steps"] if step["name"] == "add_issue_to_project")
        self.assertIn("5", project_step["command"])
        gh_calls = [call for call in run.call_args_list if call.args[0][0] == "gh"]
        self.assertTrue(all(call.kwargs["env"]["GH_TOKEN"] == "secret-token" for call in gh_calls))

    def test_github_publish_post_requires_token_for_real_run(self):
        with tempfile.TemporaryDirectory() as workspace:
            post_path = self.write_post_markdown(Path(workspace))
            args = self.publish_args(post_path, dry_run=False)

            with patch.dict("os.environ", {}, clear=True):
                with self.assertLogs("scripts.github_publish", level="ERROR") as logs:
                    with self.assertRaises(CodexJsonError):
                        run_github_publish_post(args, stdout=io.StringIO())

        self.assertIn("GitHub token environment variable is missing", "\n".join(logs.output))

    def test_github_publish_post_passes_token_to_gh_commands(self):
        with tempfile.TemporaryDirectory() as workspace:
            post_path = self.write_post_markdown(Path(workspace))
            stdout = io.StringIO()
            args = self.publish_args(post_path, dry_run=False)

            def completed(stdout_text):
                return Args(returncode=0, stdout=stdout_text, stderr="")

            with patch.dict("os.environ", {"GH_FINE_GRAINED_TOKEN": "secret-token"}, clear=True):
                with patch("scripts.github_publish.subprocess.run") as run:
                    run.side_effect = [
                        completed('{"nameWithOwner":"9to5guru/wp-workflow","viewerPermission":"WRITE"}\n'),
                        completed(""),
                        completed("https://github.com/9to5guru/wp-workflow/issues/123\n"),
                        completed('{"id":"project-item"}\n'),
                        completed(""),
                        completed(""),
                        completed(""),
                        completed("https://github.com/9to5guru/wp-workflow/pull/456\n"),
                    ]

                    run_github_publish_post(args, stdout=stdout)

        output = json.loads(stdout.getvalue())
        self.assertFalse(output["dryRun"])
        self.assertEqual(output["issueUrl"], "https://github.com/9to5guru/wp-workflow/issues/123")
        self.assertEqual(output["pullRequestUrl"], "https://github.com/9to5guru/wp-workflow/pull/456")
        gh_calls = [call for call in run.call_args_list if call.args[0][0] == "gh"]
        self.assertEqual(len(gh_calls), 4)
        self.assertTrue(all(call.kwargs["env"]["GH_TOKEN"] == "secret-token" for call in gh_calls))

    def test_github_publish_post_recreates_existing_branch_before_issue_creation(self):
        with tempfile.TemporaryDirectory() as workspace:
            post_path = self.write_post_markdown(Path(workspace))
            stdout = io.StringIO()
            args = self.publish_args(post_path, dry_run=False)

            def completed(stdout_text):
                return Args(returncode=0, stdout=stdout_text, stderr="")

            with patch.dict("os.environ", {"GH_FINE_GRAINED_TOKEN": "secret-token"}, clear=True):
                with patch("scripts.github_publish.subprocess.run") as run:
                    run.side_effect = [
                        completed('{"nameWithOwner":"9to5guru/wp-workflow","viewerPermission":"WRITE"}\n'),
                        Args(
                            returncode=128,
                            stdout="",
                            stderr=(
                                "fatal: a branch named "
                                "'feat/publish-focused-reviews-catch-risk-earlier' already exists"
                            ),
                        ),
                        completed(""),
                        completed("Deleted branch feat/publish-focused-reviews-catch-risk-earlier\n"),
                        completed(""),
                        completed("https://github.com/9to5guru/wp-workflow/issues/123\n"),
                        completed('{"id":"project-item"}\n'),
                        completed(""),
                        completed(""),
                        completed(""),
                        completed("https://github.com/9to5guru/wp-workflow/pull/456\n"),
                    ]

                    run_github_publish_post(args, stdout=stdout)

        output = json.loads(stdout.getvalue())
        branch_step = output["steps"][0]
        self.assertEqual(branch_step["name"], "create_branch")
        self.assertTrue(branch_step["recreatedExistingBranch"])
        self.assertEqual(
            branch_step["baseSwitchCommand"],
            ["git", "switch", "main"],
        )
        self.assertEqual(
            branch_step["deleteCommand"],
            ["git", "branch", "-D", "feat/publish-focused-reviews-catch-risk-earlier"],
        )
        self.assertEqual(
            branch_step["command"],
            ["git", "switch", "-c", "feat/publish-focused-reviews-catch-risk-earlier", "main"],
        )
        self.assertEqual(run.call_args_list[1].args[0][:3], ["git", "switch", "-c"])
        self.assertEqual(
            run.call_args_list[2].args[0],
            ["git", "switch", "main"],
        )
        self.assertEqual(
            run.call_args_list[3].args[0],
            ["git", "branch", "-D", "feat/publish-focused-reviews-catch-risk-earlier"],
        )
        self.assertEqual(run.call_args_list[4].args[0][:3], ["git", "switch", "-c"])
        self.assertEqual(run.call_args_list[5].args[0][:3], ["gh", "issue", "create"])
        self.assertIn("add_issue_to_project", [step["name"] for step in output["steps"]])
        self.assertIn("create_issue", [step["name"] for step in output["steps"]])

    def test_github_publish_post_explains_repository_access_failure(self):
        with tempfile.TemporaryDirectory() as workspace:
            post_path = self.write_post_markdown(Path(workspace))
            args = self.publish_args(post_path, dry_run=False)

            with patch.dict("os.environ", {"GH_FINE_GRAINED_TOKEN": "secret-token"}, clear=True):
                with patch("scripts.github_publish.subprocess.run") as run:
                    run.return_value = Args(
                        returncode=1,
                        stdout="",
                        stderr=(
                            "GraphQL: Could not resolve to a Repository with the name "
                            "'9to5guru/wp-workflow'. (repository)"
                        ),
                    )

                    with self.assertRaises(CodexJsonError) as raised:
                        run_github_publish_post(args, stdout=io.StringIO())

        message = str(raised.exception)
        self.assertIn(
            "GitHub token from GH_FINE_GRAINED_TOKEN cannot access 9to5guru/wp-workflow",
            message,
        )
        self.assertIn("organization SSO", message)
        self.assertEqual(run.call_args.args[0][:3], ["gh", "repo", "view"])

    def test_publish_github_dry_run_finds_pending_posts(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            post_path = self.write_post_markdown(root, status="pending")
            response = self.post_response()
            response["status"] = "pending"
            response["markdown"] = str(post_path.relative_to(root))
            self.write_posts_index(root, [post_index_entry(response)])
            stdout = io.StringIO()
            previous_cwd = os.getcwd()
            try:
                os.chdir(root)
                run_publish_github(self.publish_github_args(), stdout=stdout)
            finally:
                os.chdir(previous_cwd)

        output = json.loads(stdout.getvalue())
        self.assertTrue(output["dryRun"])
        self.assertEqual(output["fromStatus"], "pending")
        self.assertEqual(output["toStatus"], "PR")
        self.assertEqual(output["postCount"], 1)
        self.assertEqual(output["posts"][0]["post"]["markdown"], str(post_path.relative_to(root)))
        self.assertIn("update_post_status", [step["name"] for step in output["posts"][0]["steps"]])

    def test_publish_github_updates_pending_post_to_pr_after_publish_steps(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            post_path = self.write_post_markdown(root, status="pending")
            response = self.post_response()
            response["status"] = "pending"
            response["markdown"] = str(post_path.relative_to(root))
            index_path = self.write_posts_index(root, [post_index_entry(response)])
            stdout = io.StringIO()
            args = self.publish_github_args(dry_run=False)

            def completed(stdout_text):
                return Args(returncode=0, stdout=stdout_text, stderr="")

            previous_cwd = os.getcwd()
            try:
                os.chdir(root)
                with patch.dict("os.environ", {"GH_FINE_GRAINED_TOKEN": "secret-token"}, clear=True):
                    with patch("scripts.github_publish.subprocess.run") as run:
                        run.side_effect = [
                            completed('{"nameWithOwner":"9to5guru/wp-workflow","viewerPermission":"WRITE"}\n'),
                            completed(""),
                            completed("https://github.com/9to5guru/wp-workflow/issues/123\n"),
                            completed('{"id":"project-item"}\n'),
                            completed(""),
                            completed(""),
                            completed(""),
                            completed("https://github.com/9to5guru/wp-workflow/pull/456\n"),
                            completed(""),
                            completed(""),
                            completed(""),
                        ]

                        run_publish_github(args, stdout=stdout)
            finally:
                os.chdir(previous_cwd)

            output = json.loads(stdout.getvalue())
            self.assertFalse(output["dryRun"])
            self.assertEqual(output["postCount"], 1)
            step_names = [step["name"] for step in output["posts"][0]["steps"]]
            self.assertEqual(
                step_names,
                [
                    "create_branch",
                    "create_issue",
                    "add_issue_to_project",
                    "stage_post",
                    "commit_post",
                    "push_branch",
                    "create_pull_request",
                    "update_post_status",
                    "stage_status",
                    "commit_status",
                    "push_status",
                ],
            )
            index = json.loads(index_path.read_text(encoding="utf-8"))
            self.assertEqual(index["posts"][0]["status"], "PR")
            self.assertIn('status: "PR"', post_path.read_text(encoding="utf-8"))
            gh_calls = [call for call in run.call_args_list if call.args[0][0] == "gh"]
            self.assertEqual(len(gh_calls), 4)
            self.assertTrue(all(call.kwargs["env"]["GH_TOKEN"] == "secret-token" for call in gh_calls))

    def test_linkedin_carousel_generate_renders_static_presentation_without_pdf(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            source_dir = root / "linkedin-carousel"
            source_dir.mkdir()
            (source_dir / "data.json").write_text("[]", encoding="utf-8")
            (source_dir / "index.html").write_text(
                '<html><body><main class="presentation"><section id="slide-1">Slide 1</section></main></body></html>',
                encoding="utf-8",
            )
            stdout = io.StringIO()
            args = Args(
                source_dir=str(source_dir),
                data="data.json",
                template="index.html",
                output_dir="output",
                no_pdf=True,
                pretty=False,
            )

            run_linkedin_carousel_generate(args, stdout=stdout)

            output = json.loads(stdout.getvalue())
            html_path = source_dir / "output" / "carousel.html"
            self.assertEqual(output["html"], str(html_path))
            self.assertIsNone(output["pdf"])
            self.assertEqual(output["pdfSkipped"], "disabled by --no-pdf")
            self.assertIn('class="presentation"', html_path.read_text(encoding="utf-8"))
            self.assertIn('id="slide-1"', html_path.read_text(encoding="utf-8"))

    def test_linkedin_carousel_generate_renders_html_without_pdf(self):
        with tempfile.TemporaryDirectory() as workspace:
            root = Path(workspace)
            source_dir = root / "linkedin-carousel"
            source_dir.mkdir()
            (source_dir / "data.json").write_text(
                json.dumps(
                    [
                        {
                            "category": "Protocol",
                            "title": "MCP",
                            "subtitle": "Model Context Protocol",
                            "description": "Tool discovery for AI applications.",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            (source_dir / "template.html").write_text(
                "<html><body>{% for s in slides %}<h1>{{ s.title }}</h1>{% endfor %}</body></html>",
                encoding="utf-8",
            )
            stdout = io.StringIO()
            args = Args(
                source_dir=str(source_dir),
                data="data.json",
                template="template.html",
                output_dir="output",
                no_pdf=True,
                pretty=False,
            )

            run_linkedin_carousel_generate(args, stdout=stdout)

            output = json.loads(stdout.getvalue())
            html_path = source_dir / "output" / "carousel.html"
            self.assertEqual(output["html"], str(html_path))
            self.assertIsNone(output["pdf"])
            self.assertEqual(output["pdfSkipped"], "disabled by --no-pdf")
            self.assertIn("<h1>MCP</h1>", html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
