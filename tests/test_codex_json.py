import unittest

from scripts.codex_json import CodexJsonError, extract_json, select_field


TRANSCRIPT = """OpenAI Codex v0.144.5
--------
user
write linkedin post about idempotency, respond in json
codex
{
  "post": "Idempotency makes retries safe."
}
"""


class CodexJsonTests(unittest.TestCase):
    def test_extracts_last_json_object_from_transcript(self):
        self.assertEqual(
            extract_json(TRANSCRIPT),
            {"post": "Idempotency makes retries safe."},
        )

    def test_selects_dotted_field_path(self):
        self.assertEqual(select_field({"items": [{"post": "hello"}]}, "items.0.post"), "hello")

    def test_raises_when_json_is_missing(self):
        with self.assertLogs("scripts.codex_json", level="ERROR") as logs:
            with self.assertRaises(CodexJsonError):
                extract_json("codex\nnot json")

        self.assertIn("No JSON candidates found", "\n".join(logs.output))


if __name__ == "__main__":
    unittest.main()
