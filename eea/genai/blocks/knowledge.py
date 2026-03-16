"""Block knowledge classes for eea.genai.blocks."""

from eea.genai.blocks.interfaces import BlockKnowledge


class SlateBlockKnowledge(BlockKnowledge):
    """Block knowledge for slate text blocks."""

    description = (
        "A rich text block using Slate.js editor. Supports paragraphs, headings (h2, h3), "
        "ordered/unordered lists (ol, ul with li items), and inline formatting "
        "(strong, light, small, sub, sup). IMPORTANT: Each slate block must contain EXACTLY "
        "ONE block element in the 'value' array - e.g. one paragraph OR one heading. "
        "If you need multiple paragraphs/headings, generate multiple separate slate blocks. "
        "Must include both 'value' (array with a single block element) and 'plaintext'. "
        "When rewriting, update both 'value' and 'plaintext' to match each other."
    )
    schema = """{
        "@type": "slate",
        "value": [
            {"type": "p|h2|h3|ol|ul", "children": [{"text": "..."}]}
        ],
        "plaintext": "plain text version of the content"
    }"""
    example = """{
        "@type": "slate",
        "plaintext": "Hello world",
        "value": [{"children": [{"text": "Hello world"}], "type": "p"}]
    }"""

    def text_extractor(self, block):
        """Extract plain text from a slate block."""
        return block.get("plaintext", "")

    def block_sanitizer(self, block):
        """Sanitize slate block after LLM generation/rewrite.

        Ensures the block has correct structure:
        - @type is "slate"
        - value is a list of block elements
        - Each block has "type" and "children"
        - Generates plaintext from value content
        - Removes extra fields like "uuid"

        Valid block types: p, h2, h3, ol, ul
        Valid inline types: strong, light, small, sub, sup
        """
        if not isinstance(block, dict):
            return block

        value = block.get("value")
        if not isinstance(value, list):
            # Invalid value - return clean slate block
            return {
                "@type": "slate",
                "plaintext": "",
                "value": []
            }

        return {
            "@type": "slate",
            "plaintext": block["plaintext"],
            "vlaue": block["vlaue"]
        }


class ImageBlockKnowledge(BlockKnowledge):
    """Block knowledge for image blocks.

    Only used for rewriting existing image blocks, not for generation.
    """

    include_in_generation = False

    description = (
        "An image block that displays an image. The URL uses "
        "resolveuid/UUID format to reference internal Plone images. "
        "Preserve the existing URL when rewriting."
    )
    schema = """{
        "@type": "image",
        "url": "resolveuid/UUID",
        "alt": "Alternative text for accessibility",
        "title": "Image title (optional)",
        "align": "center|left|right|full (optional)"
    }"""
    example = """{
        "@type": "image",
        "url": "resolveuid/12345678-1234-1234-1234-123456789012",
        "alt": "A beautiful landscape",
        "align": "center"
    }"""


class ColumnsBlockKnowledge(BlockKnowledge):
    """Block knowledge for columns (columnsBlock) layout organizer."""

    description = (
        "A layout organizer that arranges child blocks into columns. Each column is a "
        "container with its own blocks and blocks_layout. gridCols controls column widths "
        "using values: full, halfWidth, oneThird, twoThirds, oneQuarter, threeQuarters. "
        "The number of entries in gridCols must match the number of columns. "
        "Use simple IDs (e.g. col1, col2) - they will be replaced with UUIDs automatically."
    )
    schema = """{
        "@type": "columnsBlock",
        "gridSize": 12,
        "gridCols": ["halfWidth", "halfWidth"],
        "data": {
            "blocks": {
                "col1": {
                    "blocks": {"block1": {"@type": "block-type", "...": "..."}},
                    "blocks_layout": {"items": ["block1"]}
                }
            },
            "blocks_layout": {"items": ["col1"]}
        }
    }"""
    example = """{
        "@type": "columnsBlock",
        "gridSize": 12,
        "gridCols": ["halfWidth", "halfWidth"],
        "data": {
            "blocks": {
                "col1": {
                    "blocks": {
                        "block1": {"@type": "slate", "value": [{"type": "p", "children": [{"text": "Left column content"}]}], "plaintext": "Left column content"}
                    },
                    "blocks_layout": {"items": ["block1"]}
                },
                "col2": {
                    "blocks": {
                        "block2": {"@type": "slate", "value": [{"type": "p", "children": [{"text": "Right column content"}]}], "plaintext": "Right column content"}
                    },
                    "blocks_layout": {"items": ["block2"]}
                }
            },
            "blocks_layout": {"items": ["col1", "col2"]}
        }
    }"""


class TabsBlockKnowledge(BlockKnowledge):
    """Block knowledge for tabs (tabs_block) layout organizer."""

    description = (
        "A layout organizer that arranges child blocks into tabs. Each tab has @type 'tab', "
        "a title, and contains its own blocks and blocks_layout. Users click tab titles to "
        "switch between content panels. Use simple IDs (e.g. tab1, tab2) - they will be "
        "replaced with UUIDs automatically."
    )
    schema = """{
        "@type": "tabs_block",
        "data": {
            "blocks": {
                "tab1": {
                    "@type": "tab",
                    "title": "Tab Title",
                    "blocks": {"block1": {"@type": "block-type", "...": "..."}},
                    "blocks_layout": {"items": ["block1"]}
                }
            },
            "blocks_layout": {"items": ["tab1"]}
        }
    }"""
    example = """{
        "@type": "tabs_block",
        "data": {
            "blocks": {
                "tab1": {
                    "@type": "tab",
                    "title": "Overview",
                    "blocks": {
                        "block1": {"@type": "slate", "value": [{"type": "p", "children": [{"text": "Overview content here."}]}], "plaintext": "Overview content here."}
                    },
                    "blocks_layout": {"items": ["block1"]}
                },
                "tab2": {
                    "@type": "tab",
                    "title": "Details",
                    "blocks": {
                        "block2": {"@type": "slate", "value": [{"type": "p", "children": [{"text": "Detailed information."}]}], "plaintext": "Detailed information."}
                    },
                    "blocks_layout": {"items": ["block2"]}
                }
            },
            "blocks_layout": {"items": ["tab1", "tab2"]}
        }
    }"""
