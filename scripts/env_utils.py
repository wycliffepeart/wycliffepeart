"""Dotenv file and environment variable helpers."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from scripts.codex_json import CodexJsonError

try:
    from dotenv import load_dotenv as python_dotenv_load
except ImportError:
    python_dotenv_load = None

LOGGER = logging.getLogger(__name__)


def load_environment_file(path: Optional[str]) -> None:
    if not path:
        return

    env_path = Path(path)
    if not env_path.exists():
        LOGGER.info("Skipping missing dotenv file: path=%s", env_path)
        return

    LOGGER.info("Loading dotenv file: path=%s", env_path)
    if python_dotenv_load is not None:
        python_dotenv_load(env_path, override=False)
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, raw_value = stripped.split("=", 1)
        key = key.strip()
        value = raw_value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def env_int(name: str) -> Optional[int]:
    value = os.environ.get(name)
    if value is None or not value.strip():
        return None
    try:
        return int(value)
    except ValueError as exc:
        LOGGER.error("Environment variable must be an integer: name=%s value=%s", name, value)
        raise CodexJsonError(f"{name} must be an integer.") from exc
