#!/usr/bin/env python3
"""Project deployment CLI."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
RESUME_TO_PDF_SCRIPT = APP_DIR / "scripts" / "resume_to_pdf.py"
TERRAFORM_DIR = APP_DIR / "terraform"
RESUME_TO_PDF = None


def load_resume_to_pdf() -> ModuleType:
    global RESUME_TO_PDF

    if RESUME_TO_PDF is not None:
        return RESUME_TO_PDF

    spec = importlib.util.spec_from_file_location("wp_profile_resume_to_pdf", RESUME_TO_PDF_SCRIPT)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load resume PDF script: {RESUME_TO_PDF_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    RESUME_TO_PDF = module
    return module


RESUME_TO_PDF_MODULE = load_resume_to_pdf()
DEFAULT_INPUT = RESUME_TO_PDF_MODULE.DEFAULT_INPUT
DEFAULT_OUTPUT = RESUME_TO_PDF_MODULE.DEFAULT_OUTPUT


def run_command(command: Sequence[str], cwd: Path) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def generate_resume_pdf(args: argparse.Namespace) -> None:
    load_resume_to_pdf().convert_to_pdf(args.input, args.output, args.browser, args.timeout)
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


def run_app(args: argparse.Namespace) -> None:
    run_command(
        [
            sys.executable,
            "-m",
            "http.server",
            str(args.port),
            "--bind",
            args.host,
            "--directory",
            str(APP_DIR),
        ],
        ROOT,
    )


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

    run_parser = subparsers.add_parser("run", help="Serve the static app locally.")
    run_parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind.")
    run_parser.add_argument("--port", type=int, default=8000, help="Port to serve on.")
    run_parser.set_defaults(func=run_app)

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


def resume_to_pdf_main() -> int:
    return load_resume_to_pdf().main()


if __name__ == "__main__":
    raise SystemExit(main())
