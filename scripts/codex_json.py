"""Extract JSON payloads from Codex transcript output."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from json import JSONDecodeError
from typing import Any, Iterable

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class JsonCandidate:
    """A JSON value found inside a larger text blob."""

    value: Any
    start: int
    end: int


class CodexJsonError(ValueError):
    """Raised when a Codex transcript does not contain extractable JSON."""


def iter_json_candidates(text: str) -> Iterable[JsonCandidate]:
    """Yield JSON objects or arrays embedded in arbitrary transcript text."""

    LOGGER.info("Scanning text for JSON candidates: chars=%s", len(text))
    decoder = json.JSONDecoder()
    index = 0
    candidate_count = 0
    decode_error_count = 0

    while index < len(text):
        next_object = text.find("{", index)
        next_array = text.find("[", index)
        starts = [pos for pos in (next_object, next_array) if pos != -1]

        if not starts:
            LOGGER.info(
                "Finished JSON candidate scan: candidates=%s decodeErrors=%s finalIndex=%s",
                candidate_count,
                decode_error_count,
                index,
            )
            return

        start = min(starts)
        LOGGER.info("Attempting JSON decode candidate: start=%s", start)

        try:
            value, end = decoder.raw_decode(text[start:])
        except JSONDecodeError as exc:
            decode_error_count += 1
            LOGGER.info(
                "Skipping invalid JSON candidate: start=%s errorPosition=%s error=%s",
                start,
                exc.pos,
                exc.msg,
            )
            index = start + 1
            continue

        candidate_count += 1
        LOGGER.info(
            "Decoded JSON candidate: number=%s start=%s end=%s type=%s",
            candidate_count,
            start,
            start + end,
            type(value).__name__,
        )
        yield JsonCandidate(value=value, start=start, end=start + end)
        index = start + end

    LOGGER.info(
        "Finished JSON candidate scan at end of text: candidates=%s decodeErrors=%s finalIndex=%s",
        candidate_count,
        decode_error_count,
        index,
    )


def extract_json(text: str, *, last: bool = True) -> Any:
    """Extract a JSON value from Codex output.

    Codex transcripts usually contain labels, prompt text, and then an assistant
    response with a JSON object. This function scans the full transcript and
    returns the last JSON value by default because the assistant response is
    typically the final structured payload in the text.
    """

    LOGGER.info("Extracting JSON from text: chars=%s select=%s", len(text), "last" if last else "first")
    candidates = list(iter_json_candidates(text))
    LOGGER.info("JSON candidate extraction completed: candidateCount=%s", len(candidates))

    if not candidates:
        LOGGER.error("No JSON candidates found in text: chars=%s", len(text))
        raise CodexJsonError("No JSON object or array found in Codex output.")

    selected_index = -1 if last else 0
    selected = candidates[selected_index]
    LOGGER.info(
        "Selected JSON candidate: start=%s end=%s type=%s",
        selected.start,
        selected.end,
        type(selected.value).__name__,
    )
    return selected.value


def summarize_json_value(value: Any) -> str:
    if isinstance(value, dict):
        return f"dict keys={list(value.keys())}"
    if isinstance(value, list):
        return f"list length={len(value)}"
    return type(value).__name__


def select_field(value: Any, field_path: str) -> Any:
    """Select a dotted field path from a JSON-compatible value."""

    LOGGER.info("Selecting JSON field path: fieldPath=%s rootType=%s", field_path, type(value).__name__)
    current = value

    for part in field_path.split("."):
        LOGGER.info("Selecting JSON field path part: part=%s currentType=%s", part, type(current).__name__)
        if isinstance(current, dict):
            try:
                current = current[part]
            except KeyError as exc:
                LOGGER.error("Missing JSON field while selecting path: part=%s", part)
                raise CodexJsonError(f"Missing JSON field: {part}") from exc
            LOGGER.info("Selected JSON object field: part=%s nextType=%s", part, type(current).__name__)
            continue

        if isinstance(current, list):
            try:
                current = current[int(part)]
            except (ValueError, IndexError) as exc:
                LOGGER.error("Invalid JSON list index while selecting path: part=%s length=%s", part, len(current))
                raise CodexJsonError(f"Invalid JSON list index: {part}") from exc
            LOGGER.info("Selected JSON list index: part=%s nextType=%s", part, type(current).__name__)
            continue

        LOGGER.error(
            "Cannot continue JSON field selection: part=%s currentType=%s",
            part,
            type(current).__name__,
        )
        raise CodexJsonError(f"Cannot select field '{part}' from {type(current).__name__}.")

    LOGGER.info("Completed JSON field path selection: fieldPath=%s resultType=%s", field_path, type(current).__name__)
    return current
