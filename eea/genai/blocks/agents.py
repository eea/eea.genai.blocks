"""Agent configurations for generating blocks."""

from eea.genai.core.interfaces import AgentConfiguration


BLOCKS_GENERATOR_SYSTEM_PROMPT = """\
You are a content editor for the Plone CMS.
You will create structured JSON blocks from user descriptions.
Each block is a complete JSON object with "@type" and all its required fields.
You MUST only use the block types provided in this prompt.
For block IDs in "blocks" dicts and "blocks_layout.items", use simple \
placeholder strings (e.g. "1", "2", "col1", "tab1"). DO NOT use \
UUID4 format - these will be automatically replaced with proper \
UUIDs after generation.
DO NOT add a "uuid" field inside blocks - the block ID is \
the key in the blocks dict.
"""

BLOCKS_REWRITER_SYSTEM_PROMPT = """\
You are a content editor for the Plone CMS.
You will receive JSON containing CMS block(s).
Rewrite the text content according to the requested style.
Preserve the EXACT JSON structure and ALL non-text fields including:

- Block IDs (dict keys in "blocks" and "blocks_layout.items")
- Block type (@type) and all structural fields \
(gridSize, gridCols, title, etc.)

Only modify human-readable text content within the blocks.
If blocks contain nested child blocks, rewrite the text inside them as well.
"""


class BlocksGeneratorAgent(AgentConfiguration):
    """Multi-block generator agent."""

    system_prompt = BLOCKS_GENERATOR_SYSTEM_PROMPT
    task_prompt = "Generate multiple Volto blocks for the user's content request."
    skills = ["blocks_knowledge"]
    context_providers = ["generic_metadata", "blocks"]
    output_type = "eea.genai.blocks.models.BlockGenerationResult"


class SingleBlockGeneratorAgent(AgentConfiguration):
    """Single-block generator agent."""

    system_prompt = BLOCKS_GENERATOR_SYSTEM_PROMPT
    task_prompt = "Generate exactly one Volto block for the user's request."
    skills = ["blocks_knowledge"]
    context_providers = ["generic_metadata", "blocks"]
    output_type = "eea.genai.blocks.models.SingleBlockGenerationResult"


class BlocksRewriterAgent(AgentConfiguration):
    """Multi-block rewriter agent."""

    system_prompt = BLOCKS_REWRITER_SYSTEM_PROMPT
    task_prompt = "Rewrite the text content in the provided blocks."
    skills = ["blocks_knowledge"]
    context_providers = ["generic_metadata", "blocks"]
    output_type = "eea.genai.blocks.models.BlockRewriteResult"


class SingleBlockRewriterAgent(AgentConfiguration):
    """Single-block rewriter agent."""

    system_prompt = BLOCKS_REWRITER_SYSTEM_PROMPT
    task_prompt = "Rewrite the text content in the provided block."
    skills = ["blocks_knowledge"]
    context_providers = ["generic_metadata", "blocks"]
    output_type = "eea.genai.blocks.models.SingleBlockRewriteResult"
