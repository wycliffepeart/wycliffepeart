#!/usr/bin/env python3
"""Build the Next.js site and merge it with the content directories that
live in app/ (assets, the LinkedIn draft pipeline, and generated posts) into
one deployable static directory at site/out/.

The Next.js app and the content pipeline are kept in separate directories on
purpose: scripts/posts.py and scripts/linkedin_carousel.py hardcode paths
under app/blog/ (including inside LLM-facing validation strings), so that
content can't move. This module is the one place that knows both halves of
the site.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
APP_DIR = ROOT / "app"
OUT_DIR = SITE_DIR / "out"


def build_next_app() -> None:
    subprocess.run(["npm", "run", "build"], cwd=SITE_DIR, check=True)


def normalize_html_output() -> None:
    """Fix up Next's export layout to match the site's external URLs:
    index.html is also served at profile.html (legacy duplicate S3 key), and
    trailingSlash:true exports /resume as resume/index.html, but the resume
    modal's "Full Resume Page" link and Terraform both expect a flat
    resume.html."""
    if not OUT_DIR.exists():
        raise FileNotFoundError(f"Next.js build output not found: {OUT_DIR}. Run the Next.js build first.")

    shutil.copy2(OUT_DIR / "index.html", OUT_DIR / "profile.html")

    resume_dir = OUT_DIR / "resume"
    resume_index = resume_dir / "index.html"

    if resume_index.exists():
        shutil.move(str(resume_index), str(OUT_DIR / "resume.html"))
        shutil.rmtree(resume_dir)


def copy_content_directories() -> None:
    """Copy the content app/ owns (assets, blog content) into the merged
    output. Excludes resume.pdf, which is handled separately since deploy
    regenerates it after the resume page is built."""
    assets_dir = APP_DIR / "assets"

    if assets_dir.exists():
        shutil.copytree(assets_dir, OUT_DIR / "assets", dirs_exist_ok=True)

    blog_dir = APP_DIR / "blog"

    if blog_dir.exists():
        shutil.copytree(blog_dir, OUT_DIR / "blog", dirs_exist_ok=True)


def copy_resume_pdf() -> None:
    resume_pdf = APP_DIR / "resume.pdf"

    if resume_pdf.exists():
        shutil.copy2(resume_pdf, OUT_DIR / "resume.pdf")


def build_site() -> Path:
    """Full local-preview build: Next.js build, normalize, copy content, and
    carry over whatever resume.pdf currently exists in app/ (not
    regenerated here - see deploy() in scripts/cli.py for the deploy-time
    sequencing that regenerates it from the freshly built resume page)."""
    build_next_app()
    normalize_html_output()
    copy_content_directories()
    copy_resume_pdf()
    return OUT_DIR


def main() -> int:
    output_dir = build_site()
    print(f"Built site at {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
