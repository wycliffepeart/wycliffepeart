#!/usr/bin/env python3
"""Render resume.html to a PDF using an installed Chromium-based browser."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "resume.html"
DEFAULT_OUTPUT = ROOT / "resume.pdf"


def browser_candidates() -> list[str]:
    candidates = [
        os.environ.get("CHROME_BIN", ""),
        shutil.which("google-chrome") or "",
        shutil.which("google-chrome-stable") or "",
        shutil.which("chromium") or "",
        shutil.which("chromium-browser") or "",
        shutil.which("microsoft-edge") or "",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]

    return [candidate for candidate in candidates if candidate and Path(candidate).exists()]


def convert_to_pdf(
    input_html: Path,
    output_pdf: Path,
    browser: str | None = None,
    timeout_seconds: int = 60,
) -> None:
    input_html = input_html.resolve()
    output_pdf = output_pdf.resolve()

    if not input_html.exists():
        raise FileNotFoundError(f"Input HTML file not found: {input_html}")

    selected_browser = browser or next(iter(browser_candidates()), None)

    if not selected_browser:
        raise RuntimeError(
            "No Chromium-based browser found. Install Google Chrome/Chromium or set CHROME_BIN."
        )

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="resume-pdf-browser-") as user_data_dir:
        temporary_output = Path(user_data_dir) / output_pdf.name
        command = [
            selected_browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-extensions",
            "--no-pdf-header-footer",
            f"--user-data-dir={user_data_dir}",
            f"--print-to-pdf={temporary_output}",
            input_html.as_uri(),
        ]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        completed = wait_for_pdf(process, temporary_output, timeout_seconds)

        if completed.returncode != 0:
            raise RuntimeError(
                "Browser PDF generation failed.\n"
                f"Exit code: {completed.returncode}\n"
                f"stdout: {completed.stdout.strip()}\n"
                f"stderr: {completed.stderr.strip()}"
            )

        if not temporary_output.exists() or temporary_output.stat().st_size == 0:
            raise RuntimeError(f"PDF was not created or is empty: {temporary_output}")

        shutil.move(str(temporary_output), output_pdf)

    if not output_pdf.exists() or output_pdf.stat().st_size == 0:
        raise RuntimeError(f"PDF was not created or is empty: {output_pdf}")


def wait_for_pdf(
    process: subprocess.Popen[str],
    output_pdf: Path,
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    deadline = time.monotonic() + timeout_seconds
    last_size = -1
    stable_checks = 0

    while time.monotonic() < deadline:
        returncode = process.poll()

        if output_pdf.exists():
            current_size = output_pdf.stat().st_size
            if current_size > 0 and current_size == last_size:
                stable_checks += 1
            else:
                stable_checks = 0
                last_size = current_size

            if stable_checks >= 2:
                return finish_browser_process(process, 0)

        if returncode is not None:
            stdout, stderr = process.communicate()
            completed_returncode = 0 if output_pdf.exists() and output_pdf.stat().st_size > 0 else returncode
            return subprocess.CompletedProcess(
                process.args,
                completed_returncode,
                stdout,
                stderr,
            )

        time.sleep(0.25)

    return finish_browser_process(process, -1, timed_out=True, timeout_seconds=timeout_seconds)


def finish_browser_process(
    process: subprocess.Popen[str],
    returncode: int,
    timed_out: bool = False,
    timeout_seconds: int = 0,
) -> subprocess.CompletedProcess[str]:
    if process.poll() is None:
        process.terminate()
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
    else:
        stdout, stderr = process.communicate()

    if timed_out:
        raise RuntimeError(
            "Browser PDF generation timed out.\n"
            f"Timeout: {timeout_seconds} seconds\n"
            f"stdout: {stdout.strip()}\n"
            f"stderr: {stderr.strip()}"
        )

    return subprocess.CompletedProcess(process.args, returncode, stdout, stderr)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert resume.html to resume.pdf.")
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        convert_to_pdf(args.input, args.output, args.browser, args.timeout)
    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"Created {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
