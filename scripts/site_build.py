#!/usr/bin/env python3
"""Build the Next.js site (a static export) into out/ and copy in
workspace/resume.pdf, the one piece of deploy output the Next.js build
doesn't produce itself.

The blog is native Next.js MDX pages (content/blog/*.mdx via src/lib/blog.ts)
and images live in public/, so both are already part of `next build`'s
output. workspace/blog/ remains the Python content/LinkedIn draft pipeline's
storage location - scripts/posts.py and scripts/linkedin_carousel.py hardcode
paths under it (including inside LLM-facing validation strings) - but it is
no longer merged into the deployed site.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = ROOT / "workspace"
OUT_DIR = ROOT / "out"


def build_next_app() -> None:
    subprocess.run(["npm", "run", "build"], cwd=ROOT, check=True)


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


def copy_resume_pdf() -> None:
    resume_pdf = WORKSPACE_DIR / "resume.pdf"

    if resume_pdf.exists():
        shutil.copy2(resume_pdf, OUT_DIR / "resume.pdf")


def build_site() -> Path:
    """Full local-preview build: Next.js build, normalize, and carry over
    whatever resume.pdf currently exists in workspace/ (not regenerated here - see
    deploy() in scripts/cli.py for the deploy-time sequencing that
    regenerates it from the freshly built resume page)."""
    build_next_app()
    normalize_html_output()
    copy_resume_pdf()
    return OUT_DIR


def main() -> int:
    output_dir = build_site()
    print(f"Built site at {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
