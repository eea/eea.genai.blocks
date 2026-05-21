"""Unit tests for block knowledge sanitizers / extractors.

Pure-function tests — no Plone bootstrap required.
"""

import unittest

from eea.genai.blocks.knowledge import SlateBlockKnowledge


class TestSlateBlockSanitizer(unittest.TestCase):
    def setUp(self):
        self.kb = SlateBlockKnowledge(block_type="slate", title="Slate")

    def test_round_trip_preserves_value_and_plaintext(self):
        block = {
            "@type": "slate",
            "plaintext": "Hello world",
            "value": [{"type": "p", "children": [{"text": "Hello world"}]}],
        }
        out = self.kb.block_sanitizer(block)
        self.assertEqual(out["@type"], "slate")
        self.assertEqual(out["plaintext"], "Hello world")
        self.assertEqual(out["value"], block["value"])

    def test_strips_extra_keys(self):
        block = {
            "@type": "slate",
            "plaintext": "x",
            "value": [{"type": "p", "children": [{"text": "x"}]}],
            "uuid": "should-be-removed",
        }
        out = self.kb.block_sanitizer(block)
        self.assertNotIn("uuid", out)

    def test_invalid_value_returns_empty_slate(self):
        block = {"@type": "slate", "value": "not-a-list", "plaintext": "x"}
        out = self.kb.block_sanitizer(block)
        self.assertEqual(out, {"@type": "slate", "plaintext": "", "value": []})

    def test_missing_plaintext_defaults_to_empty(self):
        block = {
            "@type": "slate",
            "value": [{"type": "p", "children": [{"text": "x"}]}],
        }
        out = self.kb.block_sanitizer(block)
        self.assertEqual(out["plaintext"], "")
        self.assertEqual(out["value"], block["value"])

    def test_non_dict_input_returned_unchanged(self):
        self.assertEqual(self.kb.block_sanitizer("not a dict"), "not a dict")
        self.assertIsNone(self.kb.block_sanitizer(None))


class TestSlateTextExtractor(unittest.TestCase):
    def setUp(self):
        self.kb = SlateBlockKnowledge(block_type="slate", title="Slate")

    def test_extract_returns_plaintext(self):
        block = {"@type": "slate", "plaintext": "hello"}
        self.assertEqual(self.kb.text_extractor(block), "hello")

    def test_extract_missing_plaintext_returns_empty(self):
        self.assertEqual(self.kb.text_extractor({}), "")
