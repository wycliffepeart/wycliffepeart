#!/usr/bin/env python3
"""Project deployment CLI."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from scripts.resume_to_pdf import DEFAULT_INPUT, DEFAULT_OUTPUT, convert_to_pdf


ROOT = Path(__file__).resolve().parents[1]
PROFILE_APP_DIR = ROOT / "apps" / "wp-profile"
TERRAFORM_DIR = PROFILE_APP_DIR / "terraform"


def run_command(command: Sequence[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def generate_resume_pdf(args: argparse.Namespace) -> None:
    convert_to_pdf(args.input, args.output, args.browser, args.timeout)
    print(f"Created {args.output.resolve()}")


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
    generate_resume_pdf(args)

    if args.skip_init:
        print("Skipping terraform init")
    else:
        terraform_init(args)

    terraform_plan(args)

    if args.out and not args.plan_file:
        args.plan_file = args.out

    terraform_apply(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cliffe",
        description="Manage profile site deployment tasks.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    pdf_parser = subparsers.add_parser("resume-pdf", help="Generate resume.pdf from resume.html.")
    add_pdf_arguments(pdf_parser)
    pdf_parser.set_defaults(func=generate_resume_pdf)

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
        help="Primary deploy path: generate resume.pdf, then run terraform init, plan, and apply.",
    )
    add_pdf_arguments(deploy_parser)
    deploy_parser.add_argument("--skip-init", action="store_true", help="Skip terraform init.")
    deploy_parser.add_argument("--out", help="Optional Terraform plan output file.")
    deploy_parser.add_argument("--auto-approve", action="store_true", help="Pass -auto-approve to Terraform apply.")
    deploy_parser.add_argument("plan_file", nargs="?", help="Optional Terraform plan file to apply.")
    deploy_parser.set_defaults(func=deploy)

    return parser


def add_pdf_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="HTML file to render.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="PDF output path.")
    parser.add_argument(
        "--browser",
        help="Path to Chrome/Chromium. Overrides CHROME_BIN and automatic detection.",
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

    try:
        args.func(args)
    except subprocess.CalledProcessError as error:
        print(f"error: command failed with exit code {error.returncode}", file=sys.stderr)
        return error.returncode
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
