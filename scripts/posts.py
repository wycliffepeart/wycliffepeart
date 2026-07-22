"""LinkedIn post schema, validation, and persistence for Codex-generated posts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any, Optional

from scripts.codex_json import CodexJsonError, extract_json, summarize_json_value
from scripts.env_utils import env_int

LOGGER = logging.getLogger(__name__)

POST_RESPONSE_EXAMPLE = {
    "id": "fcb42734-4061-4c59-9ba4-1dac78106270",
    "title": "Idempotency Turns Retries Into Safety",
    "slug": "idempotency-turns-retries-into-safety",
    "createdAt": "2026-07-21T01:19:46Z",
    "date": "2026-07-21",
    "topic": "Backend engineering",
    "excerpt": (
        "Idempotency helps backend systems make retries safe by giving repeated commands "
        "a stable identity and predictable recovery behavior."
    ),
    "tags": [
        "backend-systems",
        "api-design",
        "idempotency",
        "reliability-engineering",
    ],
    "status": "pending",
    "markdown": "workspace/blog/linkedin/posts/2026/07/2026-07-21-011946-idempotency-turns-retries-into-safety.md",
    "body": (
        "Retries are only safe when repeating the request does not repeat the damage.\n\n"
        "Backend systems rely on retries everywhere...\n\n"
        "#BackendSystems #APIDesign #Idempotency #ReliabilityEngineering"
    ),
}

POST_INDEX_KEYS = tuple(key for key in POST_RESPONSE_EXAMPLE if key != "body")
POST_RESPONSE_REQUIRED_KEYS = tuple(POST_RESPONSE_EXAMPLE.keys())
POST_INDEX_PATH = Path("workspace/blog/linkedin/posts.json")
POST_MARKDOWN_ROOT = Path("workspace/blog/linkedin/posts")
PENDING_STATUS = "pending"
PULL_REQUEST_STATUS = "PR"
CODEX_POST_RETRIES_ENV = "WP_CODEX_POST_RETRIES"
DEFAULT_CODEX_POST_RETRIES = 5

POST_RESPONSE_INSTRUCTIONS = """

Respond only with a valid JSON object. Do not include Markdown fences, prose, or labels.
The JSON object must use exactly these keys and value types:
- id: string, a newly generated UUID.
- title: string, generated from the requested post topic.
- slug: string, generated from title in lowercase kebab-case.
- createdAt: string, the current UTC timestamp in ISO 8601 format.
- date: string, the current UTC date in YYYY-MM-DD format.
- topic: string, generated from the requested post topic.
- excerpt: string, a concise summary of the generated post.
- tags: array of strings, generated from the requested post topic.
- status: string, use pending for new generated posts.
- markdown: string, a path under workspace/blog/linkedin/posts/YYYY/MM/ using date, time, and slug.
- body: string, the complete LinkedIn post body without front matter or title heading.

Generate fresh values for every request. Do not copy sample or placeholder content.
"""


def summarize_post(value: dict) -> dict:
    return {
        "id": value.get("id"),
        "title": value.get("title"),
        "slug": value.get("slug"),
        "createdAt": value.get("createdAt"),
        "date": value.get("date"),
        "topic": value.get("topic"),
        "status": value.get("status"),
        "markdown": value.get("markdown"),
        "tagCount": len(value.get("tags", [])) if isinstance(value.get("tags"), list) else None,
        "bodyChars": len(value.get("body", "")) if isinstance(value.get("body"), str) else None,
    }


def build_codex_prompt(prompt: str) -> str:
    stripped = prompt.rstrip()
    final_prompt = f"{stripped}{POST_RESPONSE_INSTRUCTIONS}"
    LOGGER.info(
        "Built Codex prompt: inputChars=%s strippedChars=%s instructionChars=%s finalChars=%s",
        len(prompt),
        len(stripped),
        len(POST_RESPONSE_INSTRUCTIONS),
        len(final_prompt),
    )
    return final_prompt


def build_codex_retry_prompt(prompt: str, error: str, *, attempt: int, max_attempts: int) -> str:
    retry_instructions = f"""

The previous generated post failed repository validation:
{error}

Regenerate the post for retry attempt {attempt} of {max_attempts}. Use a different title,
topic angle, hook, id, slug, createdAt timestamp, markdown path, body, and hashtags.
Fix the validation error above. The id must be a canonical UUID v4 string.
Do not reuse the failed slug, failed markdown path, or any existing slug in
workspace/blog/linkedin/posts.json.
"""
    return f"{prompt.rstrip()}{retry_instructions}"


def validate_post_response(value: Any) -> dict:
    LOGGER.info("Validating Codex post response: value=%s", summarize_json_value(value))
    if not isinstance(value, dict):
        raise CodexJsonError("Codex response must be a JSON object.")

    LOGGER.info("Checking Codex post response keys: keys=%s", list(value.keys()))
    missing = [key for key in POST_RESPONSE_REQUIRED_KEYS if key not in value]
    if missing:
        LOGGER.error("Codex post response missing required fields: missing=%s", missing)
        raise CodexJsonError(f"Codex response is missing required fields: {', '.join(missing)}")
    LOGGER.info("Codex post response contains all required fields: required=%s", list(POST_RESPONSE_REQUIRED_KEYS))

    extra = [key for key in value if key not in POST_RESPONSE_REQUIRED_KEYS]
    if extra:
        LOGGER.error("Codex post response contains unexpected fields: extra=%s", extra)
        raise CodexJsonError(f"Codex response has unexpected fields: {', '.join(extra)}")
    LOGGER.info("Codex post response contains no unexpected fields")

    string_keys = [
        "id",
        "title",
        "slug",
        "createdAt",
        "date",
        "topic",
        "excerpt",
        "status",
        "markdown",
        "body",
    ]
    invalid_strings = [key for key in string_keys if not isinstance(value[key], str)]
    if invalid_strings:
        LOGGER.error("Codex post response has non-string fields: fields=%s", invalid_strings)
        raise CodexJsonError(f"Codex response fields must be strings: {', '.join(invalid_strings)}")
    LOGGER.info("Codex post response string fields validated: fields=%s", string_keys)

    if not isinstance(value["tags"], list) or not all(isinstance(tag, str) for tag in value["tags"]):
        LOGGER.error("Codex post response tags field is invalid: type=%s", type(value["tags"]).__name__)
        raise CodexJsonError("Codex response field 'tags' must be a list of strings.")
    LOGGER.info("Codex post response tags validated: tagCount=%s tags=%s", len(value["tags"]), value["tags"])

    try:
        post_uuid = uuid.UUID(value["id"])
    except ValueError as exc:
        LOGGER.error("Codex post response id is not a valid UUID: id=%s", value["id"])
        raise CodexJsonError("Codex response field 'id' must be a UUID v4 string.") from exc

    if post_uuid.version != 4:
        LOGGER.error("Codex post response id is not UUID v4: id=%s version=%s", value["id"], post_uuid.version)
        raise CodexJsonError("Codex response field 'id' must be a UUID v4 string.")

    if str(post_uuid) != value["id"].lower():
        LOGGER.error("Codex post response id is not canonical: id=%s canonical=%s", value["id"], post_uuid)
        raise CodexJsonError("Codex response field 'id' must use canonical UUID format.")
    LOGGER.info("Codex post response UUID validated: id=%s", value["id"])

    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value["slug"]):
        LOGGER.error("Codex post response slug is not kebab-case: slug=%s", value["slug"])
        raise CodexJsonError("Codex response field 'slug' must be lowercase kebab-case.")
    LOGGER.info("Codex post response slug validated: slug=%s", value["slug"])

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value["date"]):
        LOGGER.error("Codex post response date is invalid: date=%s", value["date"])
        raise CodexJsonError("Codex response field 'date' must use YYYY-MM-DD format.")
    LOGGER.info("Codex post response date validated: date=%s", value["date"])

    timestamp = re.fullmatch(
        r"(?P<date>\d{4}-\d{2}-\d{2})T(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})Z",
        value["createdAt"],
    )
    if not timestamp:
        LOGGER.error("Codex post response createdAt is invalid: createdAt=%s", value["createdAt"])
        raise CodexJsonError("Codex response field 'createdAt' must use UTC ISO 8601 format.")

    if timestamp.group("date") != value["date"]:
        LOGGER.error(
            "Codex post response createdAt/date mismatch: createdAt=%s date=%s",
            value["createdAt"],
            value["date"],
        )
        raise CodexJsonError("Codex response fields 'createdAt' and 'date' must refer to the same date.")
    LOGGER.info("Codex post response createdAt validated: createdAt=%s", value["createdAt"])

    if not value["body"].strip():
        LOGGER.error("Codex post response body is empty")
        raise CodexJsonError("Codex response field 'body' must not be empty.")
    LOGGER.info("Codex post response body validated: bodyChars=%s", len(value["body"]))

    LOGGER.info("Codex post response validation completed: post=%s", summarize_post(value))
    return value


def post_index_entry(value: dict) -> dict:
    LOGGER.info("Building posts.json index entry: post=%s", summarize_post(value))
    entry = {key: value[key] for key in POST_INDEX_KEYS}
    LOGGER.info("Built posts.json index entry: keys=%s markdown=%s", list(entry.keys()), entry["markdown"])
    return entry


def with_generated_post_status(value: dict) -> dict:
    generated = value.copy()
    generated["status"] = PENDING_STATUS
    return generated


def validate_markdown_path(value: dict) -> Path:
    LOGGER.info("Validating markdown path: markdown=%s date=%s slug=%s", value["markdown"], value["date"], value["slug"])
    markdown = Path(value["markdown"])

    if markdown.is_absolute() or ".." in markdown.parts:
        LOGGER.error("Markdown path is unsafe: markdown=%s", value["markdown"])
        raise CodexJsonError("Codex response field 'markdown' must be a safe relative path.")

    expected_parent = POST_MARKDOWN_ROOT / value["date"][0:4] / value["date"][5:7]
    if markdown.parent != expected_parent:
        LOGGER.error(
            "Markdown path parent is invalid: markdown=%s actualParent=%s expectedParent=%s",
            value["markdown"],
            markdown.parent,
            expected_parent,
        )
        raise CodexJsonError(
            "Codex response field 'markdown' must be under workspace/blog/linkedin/posts/YYYY/MM/."
        )

    time_part = value["createdAt"][11:13] + value["createdAt"][14:16] + value["createdAt"][17:19]
    expected_name = f"{value['date']}-{time_part}-{value['slug']}.md"
    if markdown.name != expected_name:
        LOGGER.error(
            "Markdown filename is invalid: actual=%s expected=%s",
            markdown.name,
            expected_name,
        )
        raise CodexJsonError(
            "Codex response field 'markdown' must use YYYY-MM-DD-HHMMSS-<slug>.md."
        )

    LOGGER.info("Markdown path validation completed: markdown=%s", markdown)
    return markdown


def quote_yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def format_post_markdown(value: dict) -> str:
    LOGGER.info(
        "Formatting markdown post: title=%s slug=%s tagCount=%s bodyChars=%s",
        value["title"],
        value["slug"],
        len(value["tags"]),
        len(value["body"]),
    )
    lines = [
        "---",
        f"id: {quote_yaml_string(value['id'])}",
        f"title: {quote_yaml_string(value['title'])}",
        f"slug: {quote_yaml_string(value['slug'])}",
        f"createdAt: {quote_yaml_string(value['createdAt'])}",
        f"topic: {quote_yaml_string(value['topic'])}",
        f"status: {quote_yaml_string(value['status'])}",
        "tags:",
    ]
    lines.extend(f"  - {quote_yaml_string(tag)}" for tag in value["tags"])
    lines.extend(
        [
            "---",
            "",
            f"# {value['title']}",
            "",
            value["body"].strip(),
            "",
        ]
    )
    markdown = "\n".join(lines)
    LOGGER.info("Formatted markdown post: markdownChars=%s", len(markdown))
    return markdown


def load_posts_index(path: Path) -> dict:
    LOGGER.info("Loading posts index: path=%s exists=%s", path, path.exists())
    if not path.exists():
        LOGGER.info("Posts index missing; initializing empty index: path=%s", path)
        return {"version": 1, "updatedAt": None, "posts": []}

    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        LOGGER.error("Posts index root is invalid: path=%s type=%s", path, type(value).__name__)
        raise CodexJsonError("workspace/blog/linkedin/posts.json must contain a JSON object.")
    if not isinstance(value.get("posts"), list):
        LOGGER.error("Posts index posts field is invalid: path=%s type=%s", path, type(value.get("posts")).__name__)
        raise CodexJsonError("workspace/blog/linkedin/posts.json must contain a posts array.")
    LOGGER.info(
        "Loaded posts index: path=%s version=%s updatedAt=%s postCount=%s",
        path,
        value.get("version"),
        value.get("updatedAt"),
        len(value["posts"]),
    )
    return value


def current_utc_timestamp() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_posts_index(path: Path, index: dict) -> None:
    LOGGER.info("Writing posts index file: path=%s postCount=%s", path, len(index.get("posts", [])))
    path.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def indexed_posts_with_status(index: dict, status: str) -> list[dict]:
    posts = [post for post in index["posts"] if isinstance(post, dict) and post.get("status") == status]
    LOGGER.info("Selected indexed posts by status: status=%s count=%s", status, len(posts))
    return posts


def replace_markdown_status(text: str, status: str) -> str:
    if not text.startswith("---\n"):
        raise CodexJsonError("Markdown post must start with YAML front matter.")

    closing = text.find("\n---\n", 4)
    if closing == -1:
        raise CodexJsonError("Markdown post front matter is not closed.")

    front_matter = text[4:closing].splitlines()
    status_line = f"status: {quote_yaml_string(status)}"
    for index, line in enumerate(front_matter):
        if re.fullmatch(r"status:\s*.*", line):
            front_matter[index] = status_line
            break
    else:
        front_matter.append(status_line)

    return "---\n" + "\n".join(front_matter) + text[closing:]


def update_indexed_post_status(
    *,
    root: Path,
    post_id: str,
    markdown: str,
    status: str,
    dry_run: bool,
) -> dict:
    LOGGER.info(
        "Updating indexed post status: postId=%s markdown=%s status=%s dryRun=%s",
        post_id,
        markdown,
        status,
        dry_run,
    )
    index_path = root / POST_INDEX_PATH
    markdown_path = root / markdown

    index = load_posts_index(index_path)
    posts = index["posts"]
    target = next((post for post in posts if isinstance(post, dict) and post.get("id") == post_id), None)
    if target is None:
        raise CodexJsonError(f"Post id was not found in {POST_INDEX_PATH}: {post_id}")

    previous_status = target.get("status")
    if not isinstance(previous_status, str):
        raise CodexJsonError(f"Post status must be a string for post id: {post_id}")

    if dry_run:
        return {
            "postId": post_id,
            "markdown": markdown,
            "fromStatus": previous_status,
            "toStatus": status,
            "index": str(POST_INDEX_PATH),
        }

    markdown_text = markdown_path.read_text(encoding="utf-8")
    updated_markdown = replace_markdown_status(markdown_text, status)
    target["status"] = status
    index["updatedAt"] = current_utc_timestamp()

    write_posts_index(index_path, index)
    markdown_path.write_text(updated_markdown, encoding="utf-8")
    LOGGER.info(
        "Indexed post status updated: postId=%s fromStatus=%s toStatus=%s",
        post_id,
        previous_status,
        status,
    )
    return {
        "postId": post_id,
        "markdown": markdown,
        "fromStatus": previous_status,
        "toStatus": status,
        "index": str(POST_INDEX_PATH),
    }


def validate_unique_post(index: dict, entry: dict) -> None:
    LOGGER.info(
        "Validating post uniqueness against posts index: id=%s slug=%s markdown=%s existingPostCount=%s",
        entry["id"],
        entry["slug"],
        entry["markdown"],
        len(index["posts"]),
    )
    posts = index["posts"]
    ids = {post.get("id") for post in posts if isinstance(post, dict)}
    slugs = {post.get("slug") for post in posts if isinstance(post, dict)}
    markdown_paths = {post.get("markdown") for post in posts if isinstance(post, dict)}

    if entry["id"] in ids:
        LOGGER.error("Duplicate post id detected: id=%s", entry["id"])
        raise CodexJsonError(f"Post id already exists: {entry['id']}")
    if entry["slug"] in slugs:
        LOGGER.error("Duplicate post slug detected: slug=%s", entry["slug"])
        raise CodexJsonError(f"Post slug already exists: {entry['slug']}")
    if entry["markdown"] in markdown_paths:
        LOGGER.error("Duplicate post markdown path detected: markdown=%s", entry["markdown"])
        raise CodexJsonError(f"Post markdown path already exists: {entry['markdown']}")
    LOGGER.info(
        "Post uniqueness validation completed: id=%s slug=%s markdown=%s",
        entry["id"],
        entry["slug"],
        entry["markdown"],
    )


def persist_post_response(value: dict, *, root: Optional[Path] = None) -> dict:
    if root is None:
        root = Path.cwd()

    LOGGER.info("Starting post persistence flow: root=%s", root)
    value = validate_post_response(value)
    value = with_generated_post_status(value)
    relative_markdown = validate_markdown_path(value)
    entry = post_index_entry(value)
    index_path = root / POST_INDEX_PATH
    markdown_path = root / relative_markdown
    LOGGER.info(
        "Resolved post persistence paths: indexPath=%s markdownPath=%s relativeMarkdown=%s",
        index_path,
        markdown_path,
        relative_markdown,
    )

    index = load_posts_index(index_path)
    validate_unique_post(index, entry)

    if markdown_path.exists():
        LOGGER.error("Markdown file already exists before write: markdown=%s", relative_markdown)
        raise CodexJsonError(f"Markdown file already exists: {relative_markdown}")

    LOGGER.info("Ensuring markdown directory exists: directory=%s", markdown_path.parent)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_text = format_post_markdown(value)
    LOGGER.info("Writing markdown file: path=%s chars=%s", markdown_path, len(markdown_text))
    markdown_path.write_text(markdown_text, encoding="utf-8")
    LOGGER.info("Markdown file write completed: path=%s", markdown_path)

    previous_updated_at = index.get("updatedAt")
    previous_count = len(index["posts"])
    LOGGER.info(
        "Updating posts index in memory: previousUpdatedAt=%s newUpdatedAt=%s previousPostCount=%s",
        previous_updated_at,
        value["createdAt"],
        previous_count,
    )
    index["updatedAt"] = value["createdAt"]
    index["posts"].append(entry)
    LOGGER.info(
        "Posts index updated in memory: newUpdatedAt=%s newPostCount=%s appendedMarkdown=%s",
        index["updatedAt"],
        len(index["posts"]),
        entry["markdown"],
    )
    index_path.parent.mkdir(parents=True, exist_ok=True)
    write_posts_index(index_path, index)
    LOGGER.info(
        "Post persistence flow completed: markdown=%s postCountBefore=%s postCountAfter=%s updatedAt=%s",
        entry["markdown"],
        previous_count,
        len(index["posts"]),
        index["updatedAt"],
    )

    return entry


def parse_front_matter(text: str) -> dict:
    LOGGER.info("Parsing Markdown front matter: chars=%s", len(text))
    if not text.startswith("---\n"):
        LOGGER.error("Markdown post missing opening front matter fence")
        raise CodexJsonError("Markdown post must start with YAML front matter.")

    closing = text.find("\n---\n", 4)
    if closing == -1:
        LOGGER.error("Markdown post missing closing front matter fence")
        raise CodexJsonError("Markdown post front matter is not closed.")

    metadata: dict[str, Any] = {}
    current_list_key: Optional[str] = None
    for line in text[4:closing].splitlines():
        if not line.strip():
            continue

        list_item = re.fullmatch(r"\s*-\s*(.+)", line)
        if list_item and current_list_key:
            metadata[current_list_key].append(parse_yaml_scalar(list_item.group(1)))
            continue

        current_list_key = None
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):(?:\s*(.*))?", line)
        if not match:
            LOGGER.error("Unsupported front matter line: line=%s", line)
            raise CodexJsonError(f"Unsupported front matter line: {line}")

        key = match.group(1)
        raw_value = match.group(2) or ""
        if raw_value:
            metadata[key] = parse_yaml_scalar(raw_value)
        else:
            metadata[key] = []
            current_list_key = key

    LOGGER.info("Parsed Markdown front matter: keys=%s", list(metadata.keys()))
    return metadata


def parse_yaml_scalar(value: str) -> str:
    stripped = value.strip()
    if stripped.startswith('"') and stripped.endswith('"'):
        try:
            decoded = json.loads(stripped)
        except json.JSONDecodeError as exc:
            LOGGER.error("Invalid quoted YAML scalar: value=%s", value)
            raise CodexJsonError(f"Invalid quoted front matter value: {value}") from exc
        if not isinstance(decoded, str):
            raise CodexJsonError(f"Front matter value must be a string: {value}")
        return decoded
    return stripped


def load_post_metadata(path: Path) -> dict:
    LOGGER.info("Loading post metadata: path=%s", path)
    if not path.exists():
        LOGGER.error("Post Markdown file does not exist: path=%s", path)
        raise CodexJsonError(f"Post Markdown file does not exist: {path}")
    if not path.is_file():
        LOGGER.error("Post Markdown path is not a file: path=%s", path)
        raise CodexJsonError(f"Post Markdown path is not a file: {path}")

    metadata = parse_front_matter(path.read_text(encoding="utf-8"))
    required = ("title", "slug", "createdAt", "status")
    missing = [key for key in required if not isinstance(metadata.get(key), str) or not metadata[key].strip()]
    if missing:
        LOGGER.error("Post Markdown front matter missing required fields: missing=%s", missing)
        raise CodexJsonError(f"Post Markdown front matter is missing required fields: {', '.join(missing)}")

    LOGGER.info(
        "Loaded post metadata: title=%s slug=%s status=%s createdAt=%s",
        metadata["title"],
        metadata["slug"],
        metadata["status"],
        metadata["createdAt"],
    )
    return metadata


def resolve_codex_post_retries(args: argparse.Namespace) -> int:
    retries = getattr(args, "retries", None)
    if retries is None:
        retries = env_int(CODEX_POST_RETRIES_ENV)
    if retries is None:
        retries = DEFAULT_CODEX_POST_RETRIES
    if retries < 0:
        raise CodexJsonError("--retries must be zero or greater.")
    return retries


def is_retryable_generated_post_error(error: CodexJsonError) -> bool:
    message = str(error)
    return message.startswith(
        (
            "No JSON object or array found in Codex output.",
            "Codex response must be a JSON object.",
            "Codex response is missing required fields:",
            "Codex response has unexpected fields:",
            "Codex response fields must be strings:",
            "Codex response field 'tags' must be a list of strings.",
            "Codex response field 'id' must be a UUID v4 string.",
            "Codex response field 'id' must use canonical UUID format.",
            "Codex response field 'slug' must be lowercase kebab-case.",
            "Codex response field 'date' must use YYYY-MM-DD format.",
            "Codex response field 'createdAt' must use UTC ISO 8601 format.",
            "Codex response fields 'createdAt' and 'date' must refer to the same date.",
            "Codex response field 'body' must not be empty.",
            "Codex response field 'markdown' must be a safe relative path.",
            "Codex response field 'markdown' must be under workspace/blog/linkedin/posts/YYYY/MM/.",
            "Codex response field 'markdown' must use YYYY-MM-DD-HHMMSS-<slug>.md.",
            "Post id already exists:",
            "Post slug already exists:",
            "Post markdown path already exists:",
            "Markdown file already exists:",
        )
    )


def run_codex_post_generation(args: argparse.Namespace, prompt: str, *, attempt: int, max_attempts: int) -> dict:
    LOGGER.info(
        "Running Codex command: codex_bin=%s attempt=%s maxAttempts=%s command=%s",
        args.codex_bin,
        attempt,
        max_attempts,
        [args.codex_bin, "e", "<prompt>"],
    )
    completed = subprocess.run(
        [args.codex_bin, "e", prompt],
        check=False,
        capture_output=True,
        text=True,
    )
    LOGGER.info(
        "Codex command completed: returncode=%s stdoutChars=%s stderrChars=%s attempt=%s maxAttempts=%s",
        completed.returncode,
        len(completed.stdout),
        len(completed.stderr),
        attempt,
        max_attempts,
    )

    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "Codex command failed."
        LOGGER.error("Codex command failed: returncode=%s message=%s", completed.returncode, message)
        raise CodexJsonError(message)

    LOGGER.info("Extracting JSON from Codex stdout: attempt=%s maxAttempts=%s", attempt, max_attempts)
    value = validate_post_response(extract_json(completed.stdout))
    value = with_generated_post_status(value)
    LOGGER.info("Codex stdout response validated: post=%s", summarize_post(value))
    return value
