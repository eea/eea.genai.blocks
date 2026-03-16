"""Block rewriting using agent system."""

import json
from zope.component import queryUtility

from eea.genai.core.interfaces import IAgentExecutor
from eea.genai.core.agent import AgentDeps
from eea.genai.blocks.sanitizers import sanitize_block


DEFAULT_STYLE = "clearer, more concise, and more accessible"


def _get_agent_executor():
    """Get the agent executor utility."""
    executor = queryUtility(IAgentExecutor)
    if executor is None:
        raise RuntimeError("No IAgentExecutor utility registered")
    return executor


def rewrite_blocks(blocks, style=None, context=None, request=None):
    """Rewrite text content in multiple blocks using agents.

    Uses the ZCML-registered 'block_rewriter' agent (overridable via control panel).
    """
    executor = _get_agent_executor()

    prompt = f"Rewrite the text content in these blocks:\n{json.dumps(blocks, indent=2)}"
    if style:
        prompt += f"\n\nThe rewrite style must be: {style}."

    result = executor.run_with_agent(
        "block_rewriter",
        user_prompt=prompt,
        deps=AgentDeps(context=context, request=request),
    )

    rewritten_blocks = result.blocks
    for uid in rewritten_blocks:
        block = rewritten_blocks[uid]
        rewritten_blocks[uid] = sanitize_block(block)

    return {"blocks": rewritten_blocks}


def rewrite_block(block, style=None, context=None, request=None):
    """Rewrite text content in a single block using agents."""
    executor = _get_agent_executor()

    prompt = f"Rewrite the text content in this block:\n{json.dumps(block, indent=2)}"
    if style:
        prompt += f"\n\nThe rewrite style must be: {style}."

    result = executor.run_with_agent(
        "block_rewriter_single",
        user_prompt=prompt,
        deps=AgentDeps(context=context, request=request),
    )

    rewritten_block = sanitize_block(result.block)
    return {"block": rewritten_block}
