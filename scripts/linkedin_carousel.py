"""LinkedIn carousel command implementation."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any, TextIO

from scripts.codex_json import CodexJsonError

LOGGER = logging.getLogger(__name__)

LINKEDIN_CAROUSEL_ROOT = Path("linkedin-carousel")
LINKEDIN_CAROUSEL_DATA = Path("data.json")
LINKEDIN_CAROUSEL_TEMPLATE = Path("index.html")
LINKEDIN_CAROUSEL_OUTPUT = Path("output")
LINKEDIN_CAROUSEL_HTML = "carousel.html"
LINKEDIN_CAROUSEL_PDF = "carousel.pdf"
LINKEDIN_CAROUSEL_VIEWPORT = {"width": 1080, "height": 1350}
JINJA_MARKERS = ("{{", "{%", "{#")


def add_linkedin_carousel_parser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    linkedin_carousel = subparsers.add_parser(
        "linkedin-carousel",
        help="generate LinkedIn carousel HTML and optional PDF output",
    )
    linkedin_carousel_subparsers = linkedin_carousel.add_subparsers(
        dest="linkedin_carousel_command",
        required=True,
    )
    linkedin_carousel_generate = linkedin_carousel_subparsers.add_parser(
        "generate",
        help="render a LinkedIn carousel from JSON data and an HTML template",
    )
    linkedin_carousel_generate.add_argument(
        "--source-dir",
        default=str(LINKEDIN_CAROUSEL_ROOT),
        help="directory containing the default carousel data and template files",
    )
    linkedin_carousel_generate.add_argument(
        "--data",
        default=str(LINKEDIN_CAROUSEL_DATA),
        help="carousel slide JSON file. Relative paths are resolved inside --source-dir.",
    )
    linkedin_carousel_generate.add_argument(
        "--template",
        default=str(LINKEDIN_CAROUSEL_TEMPLATE),
        help="carousel HTML presentation/template. Relative paths are resolved inside --source-dir.",
    )
    linkedin_carousel_generate.add_argument(
        "--output-dir",
        default=str(LINKEDIN_CAROUSEL_OUTPUT),
        help="output directory. Relative paths are resolved inside --source-dir.",
    )
    linkedin_carousel_generate.add_argument(
        "--no-pdf",
        action="store_true",
        help="skip Playwright PDF export and generate only the HTML file",
    )
    linkedin_carousel_generate.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )

    return linkedin_carousel_generate


def summarize_args(args: argparse.Namespace) -> dict:
    return vars(args).copy()


def write_value(value: Any, *, pretty: bool, stdout: TextIO) -> None:
    if pretty:
        stdout.write(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        stdout.write(json.dumps(value, separators=(",", ":"), ensure_ascii=False))
    stdout.write("\n")


def resolve_linkedin_carousel_path(source_dir: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return source_dir / path


def load_linkedin_carousel_slides(path: Path) -> list:
    LOGGER.info("Loading LinkedIn carousel data: path=%s", path)
    slides = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(slides, list):
        raise CodexJsonError("LinkedIn carousel data must be a JSON array.")
    LOGGER.info("Loaded LinkedIn carousel data: path=%s slideCount=%s", path, len(slides))
    return slides


def template_uses_jinja(source: str) -> bool:
    return any(marker in source for marker in JINJA_MARKERS)


def render_linkedin_carousel_html(*, data_path: Path, template_path: Path) -> str:
    template_source = template_path.read_text(encoding="utf-8")
    if not template_uses_jinja(template_source):
        LOGGER.info("Using static LinkedIn carousel HTML: template=%s", template_path)
        return template_source

    try:
        from jinja2 import Environment, FileSystemLoader
    except ImportError as exc:
        raise CodexJsonError(
            "Missing dependency jinja2. Install CLI dependencies with `python -m pip install -e .`."
        ) from exc

    slides = load_linkedin_carousel_slides(data_path)
    env = Environment(loader=FileSystemLoader(str(template_path.parent)))
    template = env.get_template(template_path.name)
    return template.render(slides=slides)


def render_linkedin_carousel(
    *,
    data_path: Path,
    template_path: Path,
    output_dir: Path,
    export_pdf: bool,
) -> dict:
    LOGGER.info(
        "Rendering LinkedIn carousel: data=%s template=%s outputDir=%s exportPdf=%s",
        data_path,
        template_path,
        output_dir,
        export_pdf,
    )
    html = render_linkedin_carousel_html(data_path=data_path, template_path=template_path)

    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / LINKEDIN_CAROUSEL_HTML
    html_path.write_text(html, encoding="utf-8")
    LOGGER.info("Generated LinkedIn carousel HTML: path=%s chars=%s", html_path, len(html))

    result = {
        "html": str(html_path),
        "pdf": None,
        "pdfSkipped": None,
    }

    if not export_pdf:
        result["pdfSkipped"] = "disabled by --no-pdf"
        return result

    try:
        from playwright.sync_api import sync_playwright

        pdf_path = output_dir / LINKEDIN_CAROUSEL_PDF
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                page = browser.new_page(viewport=LINKEDIN_CAROUSEL_VIEWPORT)
                page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
                page.pdf(
                    path=str(pdf_path),
                    print_background=True,
                    prefer_css_page_size=True,
                )
            finally:
                browser.close()
        result["pdf"] = str(pdf_path)
        LOGGER.info("Generated LinkedIn carousel PDF: path=%s", pdf_path)
    except Exception as exc:
        result["pdfSkipped"] = str(exc)
        LOGGER.warning("LinkedIn carousel PDF export skipped: error=%s", exc)

    return result


def run_linkedin_carousel_generate(args: argparse.Namespace, *, stdout: TextIO) -> int:
    LOGGER.info("Starting LinkedIn carousel generation flow: args=%s", summarize_args(args))
    source_dir = Path(args.source_dir)
    data_path = resolve_linkedin_carousel_path(source_dir, args.data)
    template_path = resolve_linkedin_carousel_path(source_dir, args.template)
    output_dir = resolve_linkedin_carousel_path(source_dir, args.output_dir)

    output = render_linkedin_carousel(
        data_path=data_path,
        template_path=template_path,
        output_dir=output_dir,
        export_pdf=not args.no_pdf,
    )
    write_value(output, pretty=args.pretty, stdout=stdout)
    LOGGER.info("LinkedIn carousel generation flow completed: output=%s", output)
    return 0
