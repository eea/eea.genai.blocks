"""Block sanitization utilities: apply registered block_sanitizer after LLM generation/rewrite."""

import logging

from zope.component import queryUtility

from eea.genai.blocks.interfaces import IBlockKnowledge

logger = logging.getLogger("eea.genai.blocks")


def sanitize_block(block):
    """Apply block_sanitizer to a single block if registered.

    Args:
        block: A block dict (e.g. {"@type": "slate", ...})

    Returns:
        The block dict, potentially modified by the sanitizer.
    """
    block_type = block.get("@type", "")
    if not block_type:
        return block

    data = block.get("data")
    if isinstance(data, dict) and "blocks" in data:
        sanitize_blocks_container(data)

    if "blocks" in block and isinstance(block["blocks"], dict):
        sanitize_blocks_container(block)

    knowledge = queryUtility(IBlockKnowledge, name=block_type)
    if knowledge and knowledge.block_sanitizer:
        try:
            logger.debug("Applying block sanitizer for %s", block_type)
            return knowledge.block_sanitizer(block)
        except Exception:
            logger.debug(
                "Block sanitizer failed for block type '%s'",
                block_type,
                exc_info=True,
            )
    return block


def sanitize_blocks_container(container):
    """Recursively apply sanitizers to all blocks in a container.

    Args:
        container: A dict with 'blocks' and optionally 'blocks_layout' keys,
            e.g. a page's block structure or a column/tab container.

    The function modifies the container in place.
    """
    blocks = container.get("blocks", {})
    # Recurse into nested organizer blocks in the container
    for uid in blocks:
        block = blocks[uid]
        blocks[uid] = sanitize_block(block)
