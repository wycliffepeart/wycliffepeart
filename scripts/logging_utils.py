"""Logging configuration and stdout/stderr output helpers."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from typing import Any, Optional, TextIO

from scripts.codex_json import summarize_json_value

LOGGER = logging.getLogger(__name__)

LOG_LEVELS = ("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG")


def summarize_args(args: argparse.Namespace) -> dict:
    summary = vars(args).copy()
    if "prompt" in summary:
        summary["promptChars"] = len(summary["prompt"])
        summary["prompt"] = "<redacted>"
    if "github_token_env" in summary:
        summary["github_token_env"] = "<env name>"
    return summary


class SpringBootFormatter(logging.Formatter):
    """Format Python log records similarly to Spring Boot console logs."""

    default_msec_format = "%s.%03d"

    def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None) -> str:
        created = self.converter(record.created)
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%S", created)
        offset = time.strftime("%z", created)
        return f"{timestamp}.{int(record.msecs):03d}{offset}"

    def format(self, record: logging.LogRecord) -> str:
        spring_level = f"{record.levelname:>5}"
        thread_name = record.threadName[:15]
        logger_name = record.name[:40]
        message = record.getMessage()

        if record.exc_info:
            message = f"{message}\n{self.formatException(record.exc_info)}"

        return (
            f"{self.formatTime(record)} {spring_level} {record.process} --- "
            f"[{thread_name:>15}] {logger_name:<40} : {message}"
        )


def configure_logging(level_name: str, *, stderr: TextIO = sys.stderr) -> None:
    level = getattr(logging, level_name.upper())
    handler = logging.StreamHandler(stderr)
    handler.setFormatter(SpringBootFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(level)


def write_value(value: Any, *, pretty: bool, stdout: TextIO) -> None:
    indent = 2 if pretty else None
    LOGGER.info("Writing JSON value to stdout: value=%s pretty=%s", summarize_json_value(value), pretty)
    stdout.write(json.dumps(value, ensure_ascii=False, indent=indent))
    stdout.write("\n")
    LOGGER.info("Finished writing JSON value to stdout")


def write_error(message: str, *, stderr: TextIO) -> None:
    stderr.write(json.dumps({"error": message}, ensure_ascii=False))
    stderr.write("\n")
