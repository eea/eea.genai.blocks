"""Block generation and rewriting prompts.

System prompts are used as defaults for ZCML-registered agents.
The dynamic block types description is injected by the ``blocks_knowledge``
skill at runtime -- do NOT include {block_types_description} here.
"""

BLOCK_GEN_SYSTEM_PROMPT = """\
You are a content editor for the Plone CMS.
You will create structured JSON blocks from user descriptions.
Each block is a complete JSON object with "@type" and all its required fields.
You MUST only use the block types provided in this prompt.
For block IDs in "blocks" dicts and "blocks_layout.items", use simple placeholder \
strings (e.g. "1", "2", "col1", "tab1"). DO NOT use UUID4 format - these will be \
automatically replaced with proper UUIDs after generation.
DO NOT add a "uuid" field inside blocks - the block ID is the key in the blocks dict."""

BLOCK_GEN_USER_PROMPT_TEMPLATE = """Existing page content for context:

{page_context}

---

Create Volto blocks for the following content request:

{user_request}

Return a JSON list where each item is a block object with '@type' and all its required fields. See block type schemas below for details."""

BLOCK_GEN_SINGLE_USER_PROMPT_TEMPLATE = """Existing page content for context:

{page_context}

---

Create a single Volto block for the following request:

{user_request}

Return exactly one block object.{type_hint}"""


# Rewrite prompts
REWRITE_SYSTEM_PROMPT = """\
You are a content editor for the Plone CMS.
You will receive JSON containing CMS block(s).
Rewrite the text content according to the requested style.
Preserve the EXACT JSON structure and ALL non-text fields including:
- Block IDs (dict keys in 'blocks' and 'blocks_layout.items')
- Block type (@type) and all structural fields (gridSize, gridCols, title, etc.)
Only modify human-readable text content within the blocks.
If blocks contain nested child blocks, rewrite the text inside them as well."""

DEFAULT_STYLE = "clearer, more concise, and more accessible"

REWRITE_USER_PROMPT_TEMPLATE = """Existing page content for context:

{page_context}

---

Rewrite the text content in the following blocks:

{blocks_json}"""

REWRITE_SINGLE_USER_PROMPT_TEMPLATE = """Existing page content for context:

{page_context}

---

Rewrite the text content in the following block:

{block_json}"""
