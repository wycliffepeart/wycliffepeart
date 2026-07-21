#!/usr/bin/env python3
"""Render resume.html to a PDF using Playwright Chromium."""

from __future__ import annotations

import argparse
import functools
import http.server
import sys
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
SITE_OUT_DIR = ROOT / "site" / "out"
DEFAULT_INPUT = SITE_OUT_DIR / "resume.html"
DEFAULT_OUTPUT = APP_DIR / "resume.pdf"


class _QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: object) -> None:  # noqa: A002 - matches base signature
        pass


@contextmanager
def _serve_directory(directory: Path) -> Iterator[int]:
    """Serve `directory` over local HTTP so root-relative asset paths
    (for example Next.js's /_next/static/... chunks) resolve correctly.
    A plain file:// URI can't do this: the browser resolves root-relative
    paths against the filesystem root, not the HTML file's directory."""
    handler = functools.partial(_QuietHTTPRequestHandler, directory=str(directory))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        thread.join()


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

    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise RuntimeError(
            "Playwright is not installed. Run `python3 -m pip install -e .` "
            "and `python3 -m playwright install chromium`."
        ) from error

    try:
        with sync_playwright() as playwright:
            launch_options = {}

            if browser:
                launch_options["executable_path"] = str(Path(browser).expanduser())

            chromium = playwright.chromium.launch(**launch_options)
            try:
                page = chromium.new_page()
                page.emulate_media(media="print")

                with _serve_directory(input_html.parent) as port:
                    page.goto(
                        f"http://127.0.0.1:{port}/{input_html.name}",
                        wait_until="networkidle",
                        timeout=timeout_seconds * 1000,
                    )
                    page.evaluate(
                        "document.fonts ? document.fonts.ready : Promise.resolve()"
                    )
                    page.pdf(
                        path=str(output_pdf),
                        format="A4",
                        print_background=True,
                        prefer_css_page_size=True,
                        display_header_footer=False,
                    )
            finally:
                chromium.close()
    except PlaywrightTimeoutError as error:
        raise RuntimeError(
            f"Playwright PDF generation timed out after {timeout_seconds} seconds."
        ) from error
    except PlaywrightError as error:
        raise RuntimeError(
            "Playwright PDF generation failed. If Chromium is not installed, run "
            f"`python3 -m playwright install chromium`. Details: {error}"
        ) from error

    if not output_pdf.exists() or output_pdf.stat().st_size == 0:
        raise RuntimeError(f"PDF was not created or is empty: {output_pdf}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert resume.html to resume.pdf.")
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
