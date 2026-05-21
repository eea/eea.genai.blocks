"""Block rewriting using agent system."""

import json

from eea.genai.core.agent import AgentDeps
from eea.genai.core.utils import get_executor
from eea.genai.blocks.sanitizers import sanitize_block


DEFAULT_STYLE = "clearer, more concise, and more accessible"


def rewrite_blocks(blocks, style=None, context=None, request=None):
    """Rewrite text content in multiple blocks using agents."""
    prompt = (
        f"Rewrite the text content in these blocks:\n{json.dumps(blocks, indent=2)}"
    )
    if style:
        prompt += f"\n\nThe rewrite style must be: {style}."

    result = get_executor().run_with_agent(
        "block_rewriter",
        user_prompt=prompt,
        deps=AgentDeps(context=context, request=request),
    )

    rewritten = {uid: sanitize_block(b) for uid, b in result.blocks.items()}
    return {"blocks": rewritten}


def rewrite_block(block, style=None, context=None, request=None):
    """Rewrite text content in a single block using agents."""
    prompt = f"Rewrite the text content in this block:\n{json.dumps(block, indent=2)}"
    if style:
        prompt += f"\n\nThe rewrite style must be: {style}."

    result = get_executor().run_with_agent(
        "block_rewriter_single",
        user_prompt=prompt,
        deps=AgentDeps(context=context, request=request),
    )
    return {"block": sanitize_block(result.block)}
