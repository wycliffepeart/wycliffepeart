#!/usr/bin/env python3
"""Project CLI: site deployment plus content/LinkedIn workflow commands."""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence, TextIO

from scripts import resume_to_pdf, site_build
from scripts.codex_json import CodexJsonError, extract_json, select_field
from scripts.env_utils import load_environment_file
from scripts.github_publish import add_github_publish_options, run_github_publish_post, run_publish_github
from scripts.linkedin_carousel import add_linkedin_carousel_parser, run_linkedin_carousel_generate
from scripts.logging_utils import (
    LOG_LEVELS,
    SpringBootFormatter,
    configure_logging,
    summarize_args,
    write_error,
    write_value,
)
from scripts.posts import (
    CODEX_POST_RETRIES_ENV,
    DEFAULT_CODEX_POST_RETRIES,
    build_codex_prompt,
    build_codex_retry_prompt,
    is_retryable_generated_post_error,
    load_post_metadata,
    persist_post_response,
    post_index_entry,
    resolve_codex_post_retries,
    run_codex_post_generation,
    validate_post_response,
)

LOGGER = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = ROOT / "workspace"
TERRAFORM_DIR = ROOT / "terraform"
SITE_OUT_DIR = site_build.OUT_DIR
DEFAULT_INPUT = resume_to_pdf.DEFAULT_INPUT
DEFAULT_OUTPUT = resume_to_pdf.DEFAULT_OUTPUT


def run_command(command: Sequence[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def generate_resume_pdf(args: argparse.Namespace) -> None:
    resume_to_pdf.convert_to_pdf(args.input, args.output, args.browser, args.timeout)
    print(f"Created {args.output.resolve()}")


def build_site(_: argparse.Namespace) -> None:
    output_dir = site_build.build_site()
    print(f"Built site at {output_dir}")


def terraform_init(_: argparse.Namespace) -> None:
    run_command(["terraform", "init"], TERRAFORM_DIR)


def terraform_plan(args: argparse.Namespace) -> None:
    command = ["terraform", "plan"]

    if args.out:
        command.extend(["-out", args.out])

    run_command(command, TERRAFORM_DIR)


def terraform_apply(args: argparse.Namespace) -> None:
    command = ["terraform", "apply"]

    if args.auto_approve:
        command.append("-auto-approve")

    if args.plan_file:
        command.append(args.plan_file)

    run_command(command, TERRAFORM_DIR)


def deploy(args: argparse.Namespace) -> None:
    site_build.build_next_app()
    site_build.normalize_html_output()

    # resume.pdf is regenerated from the freshly built resume page, then
    # copied into the build output - see resume_to_pdf.DEFAULT_INPUT.
    generate_resume_pdf(args)
    site_build.copy_resume_pdf()

    if args.skip_init:
        print("Skipping terraform init")
    else:
        terraform_init(args)

    terraform_plan(args)

    if args.out and not args.plan_file:
        args.plan_file = args.out

    terraform_apply(args)


def run_app(args: argparse.Namespace) -> None:
    site_build.build_site()
    run_command(
        [
            sys.executable,
            "-m",
            "http.server",
            str(args.port),
            "--bind",
            args.host,
            "--directory",
            str(SITE_OUT_DIR),
        ],
        ROOT,
    )


def read_text(path: str, stdin: TextIO) -> str:
    if path == "-":
        LOGGER.info("Reading text from stdin")
        text = stdin.read()
        LOGGER.info("Read text from stdin: chars=%s", len(text))
        return text

    file_path = Path(path)
    LOGGER.info("Reading text file: path=%s", file_path)
    text = file_path.read_text(encoding="utf-8")
    LOGGER.info("Read text file: path=%s chars=%s", file_path, len(text))
    return text


def run_codex_json(args: argparse.Namespace, *, stdin: TextIO, stdout: TextIO) -> int:
    LOGGER.info(
        "Extracting JSON from Codex transcript: path=%s field=%s first=%s",
        args.path,
        args.field,
        args.first,
    )
    text = read_text(args.path, stdin)
    LOGGER.info("Extracting JSON value from transcript text: chars=%s last=%s", len(text), not args.first)
    value = extract_json(text, last=not args.first)
    LOGGER.info("Extracted JSON value from transcript: value=%s", value)

    if args.field:
        LOGGER.info("Selecting JSON field from extracted value: field=%s", args.field)
        value = select_field(value, args.field)
        LOGGER.info("Selected JSON field: field=%s value=%s", args.field, value)

    write_value(value, pretty=args.pretty, stdout=stdout)
    LOGGER.info("Codex JSON extraction completed")
    return 0


def run_codex_e(args: argparse.Namespace, *, stdout: TextIO) -> int:
    LOGGER.info("Starting Codex execution flow: args=%s", summarize_args(args))
    prompt = build_codex_prompt(args.prompt)
    LOGGER.info(
        "Codex execution flow prepared prompt: promptChars=%s dryRun=%s noWrite=%s",
        len(prompt),
        args.dry_run,
        args.no_write,
    )

    if args.dry_run:
        LOGGER.info("Prepared dry-run Codex command: codex_bin=%s", args.codex_bin)
        write_value({"command": [args.codex_bin, "e", prompt], "prompt": prompt}, pretty=args.pretty, stdout=stdout)
        LOGGER.info("Codex dry-run flow completed")
        return 0

    load_environment_file(getattr(args, "env_file", ".env.local"))
    retries = resolve_codex_post_retries(args)
    max_attempts = retries + 1
    LOGGER.info(
        "Codex execution retry settings resolved: noWrite=%s retries=%s maxAttempts=%s",
        args.no_write,
        retries,
        max_attempts,
    )

    output = None
    attempt_prompt = prompt
    for attempt in range(1, max_attempts + 1):
        try:
            value = run_codex_post_generation(args, attempt_prompt, attempt=attempt, max_attempts=max_attempts)
            LOGGER.info("Handling Codex post response: noWrite=%s attempt=%s", args.no_write, attempt)
            if args.no_write:
                output = post_index_entry(value)
            else:
                output = persist_post_response(value)
            break
        except CodexJsonError as exc:
            if attempt >= max_attempts or not is_retryable_generated_post_error(exc):
                raise
            LOGGER.warning(
                "Retrying Codex generation after generated post validation failure: attempt=%s nextAttempt=%s maxAttempts=%s error=%s",
                attempt,
                attempt + 1,
                max_attempts,
                exc,
            )
            attempt_prompt = build_codex_retry_prompt(prompt, str(exc), attempt=attempt + 1, max_attempts=max_attempts)

    if output is None:
        raise CodexJsonError("Codex command did not produce a post response.")

    LOGGER.info("Codex post response handled: output=%s", output)
    write_value(output, pretty=args.pretty, stdout=stdout)
    LOGGER.info("Codex execution flow completed")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wp",
        description="Manage profile site deployment and content workflow tasks.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=LOG_LEVELS,
        help="Minimum log level for stderr logs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    pdf_parser = subparsers.add_parser("pdf", help="Generate resume.pdf from the built resume page.")
    add_pdf_arguments(pdf_parser)
    pdf_parser.set_defaults(func=generate_resume_pdf)

    build_parser = subparsers.add_parser(
        "build",
        help="Build the Next.js static export into out/.",
    )
    build_parser.set_defaults(func=build_site)

    init_parser = subparsers.add_parser("init", help="Run terraform init.")
    init_parser.set_defaults(func=terraform_init)

    plan_parser = subparsers.add_parser("plan", help="Run terraform plan.")
    plan_parser.add_argument("--out", help="Optional Terraform plan output file.")
    plan_parser.set_defaults(func=terraform_plan)

    apply_parser = subparsers.add_parser("apply", help="Run terraform apply.")
    apply_parser.add_argument("--auto-approve", action="store_true", help="Pass -auto-approve to Terraform.")
    apply_parser.add_argument("plan_file", nargs="?", help="Optional Terraform plan file to apply.")
    apply_parser.set_defaults(func=terraform_apply)

    deploy_parser = subparsers.add_parser(
        "deploy",
        help=(
            "Primary deploy path: build the site, generate resume.pdf, then run "
            "terraform init, plan, and apply."
        ),
    )
    add_pdf_arguments(deploy_parser)
    deploy_parser.add_argument("--skip-init", action="store_true", help="Skip terraform init.")
    deploy_parser.add_argument("--out", help="Optional Terraform plan output file.")
    deploy_parser.add_argument("--auto-approve", action="store_true", help="Pass -auto-approve to Terraform apply.")
    deploy_parser.add_argument("plan_file", nargs="?", help="Optional Terraform plan file to apply.")
    deploy_parser.set_defaults(func=deploy)

    run_parser = subparsers.add_parser("run", help="Build the site and serve it locally.")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to serve on.")
    run_parser.set_defaults(func=run_app)

    codex_json_parser = subparsers.add_parser(
        "codex-json",
        help="Extract the assistant JSON payload from Codex transcript text.",
    )
    codex_json_parser.add_argument(
        "path",
        nargs="?",
        default="-",
        help="Transcript file path, or '-' / omitted for stdin.",
    )
    codex_json_parser.add_argument(
        "--field",
        help="Optional dotted field path to print, for example: post or choices.0.message.content.",
    )
    codex_json_parser.add_argument(
        "--first",
        action="store_true",
        help="Return the first JSON value found instead of the last.",
    )
    codex_json_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    codex_json_parser.set_defaults(func=lambda args: run_codex_json(args, stdin=sys.stdin, stdout=sys.stdout))

    codex_parser = subparsers.add_parser("codex", help="Run Codex with repository response rules.")
    codex_subparsers = codex_parser.add_subparsers(dest="codex_command", required=True)
    codex_e_parser = codex_subparsers.add_parser(
        "e",
        help="Run `codex e` and require a LinkedIn post JSON response.",
    )
    codex_e_parser.add_argument("prompt", help="Prompt to send to Codex.")
    codex_e_parser.add_argument("--codex-bin", default="codex", help="Codex executable to run.")
    codex_e_parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    codex_e_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the final prompt as JSON without running Codex.",
    )
    codex_e_parser.add_argument(
        "--no-write",
        action="store_true",
        help="Validate and print the Codex response without updating content files.",
    )
    codex_e_parser.add_argument(
        "--env-file",
        default=".env.local",
        help="Dotenv file to load before reading Codex workflow environment variables.",
    )
    codex_e_parser.add_argument(
        "--retries",
        type=int,
        help=(
            "Number of generated-post validation and persistence retries after the first Codex generation. "
            f"Defaults to {CODEX_POST_RETRIES_ENV} or {DEFAULT_CODEX_POST_RETRIES}."
        ),
    )
    codex_e_parser.set_defaults(func=lambda args: run_codex_e(args, stdout=sys.stdout))

    linkedin_carousel_generate_parser = add_linkedin_carousel_parser(subparsers)
    linkedin_carousel_generate_parser.set_defaults(
        func=lambda args: run_linkedin_carousel_generate(args, stdout=sys.stdout)
    )

    publish_parser = subparsers.add_parser("publish", help="Publish repository content.")
    publish_subparsers = publish_parser.add_subparsers(dest="publish_command", required=True)
    publish_github_parser = publish_subparsers.add_parser(
        "github",
        help="Publish all pending LinkedIn posts through GitHub CLI.",
    )
    add_github_publish_options(publish_github_parser, include_markdown=False)
    publish_github_parser.set_defaults(func=lambda args: run_publish_github(args, stdout=sys.stdout))

    github_parser = subparsers.add_parser("github", help="Publish content through GitHub CLI.")
    github_subparsers = github_parser.add_subparsers(dest="github_command", required=True)
    github_publish_post_parser = github_subparsers.add_parser(
        "publish-post",
        help="Create an issue, branch, PR, and optional project item for a LinkedIn post.",
    )
    add_github_publish_options(github_publish_post_parser, include_markdown=True)
    github_publish_post_parser.set_defaults(func=lambda args: run_github_publish_post(args, stdout=sys.stdout))

    return parser


def add_pdf_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="HTML file to render.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="PDF output path.")
    parser.add_argument(
        "--browser",
        help="Optional path to a Chrome/Chromium executable. Defaults to Playwright Chromium.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Maximum seconds to wait for the browser to generate the PDF.",
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.log_level)
    LOGGER.info("Starting wp command: command=%s args=%s", args.command, summarize_args(args))

    try:
        result = args.func(args)
    except subprocess.CalledProcessError as error:
        print(f"error: command failed with exit code {error.returncode}", file=sys.stderr)
        return error.returncode
    except (CodexJsonError, OSError) as error:
        LOGGER.error("wp command failed: command=%s error=%s", args.command, error)
        write_error(str(error), stderr=sys.stderr)
        return 1
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return result if isinstance(result, int) else 0


def resume_to_pdf_main() -> int:
    return resume_to_pdf.main()


if __name__ == "__main__":
    raise SystemExit(main())
