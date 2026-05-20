"""Agent skills for eea.genai.summary."""

import logging

from eea.genai.blocks.interfaces import IBlockKnowledge
from eea.genai.core.interfaces import Enricher
from eea.genai.core.utils import Source, batch_get_utilities

logger = logging.getLogger("eea.genai.blocks")


class BlocksContentProvider(Enricher):
    """Extracts text content from Volto blocks and adds it to the user prompt.

    Pulls plain text from all blocks on thecontent object.
    """

    name = "blocks"
    description = "Adds block text content to the user prompt"

    def user_prompt(self, deps):
        context = getattr(deps, "context")
        properties = getattr(deps, "properties", None) or {}

        if context is None:
            return ""

        source = Source(context, properties)
        block_text = extract_text(source)
        if not block_text:
            return ""
        return f"### Page content:\n\n{block_text}"


def extract_text(context):
    """Return concatenated text content from all blocks."""
    blocks = getattr(context, "blocks", None) or {}
    blocks_layout = getattr(context, "blocks_layout", None) or {}
    if not blocks:
        return ""

    container = {"blocks": blocks, "blocks_layout": blocks_layout}
    # Batch-load all block-knowledge utilities once instead of per-block
    # queryUtility lookups (was N+1 across organizer trees).
    knowledge_map = batch_get_utilities(IBlockKnowledge)
    parts = []
    for block in _iter_blocks_ordered(container):
        block_type = block.get("@type", "")
        text = _extract_block_text(block, block_type, knowledge_map)
        if text:
            parts.append(text)

    return "\n\n".join(parts)


def _extract_block_text(block, block_type, knowledge_map):
    """Extract text from a single block using registered extractors."""
    knowledge = knowledge_map.get(block_type)
    if knowledge and knowledge.text_extractor:
        try:
            return knowledge.text_extractor(block)
        except Exception:
            logger.debug(
                "Text extractor failed for block type '%s'",
                block_type,
                exc_info=True,
            )

    # Fallback: try plaintext field (common in slate blocks)
    plaintext = block.get("plaintext", "")
    if plaintext:
        return plaintext.strip()

    return ""


def _iter_blocks_ordered(blocks_container):
    """Yield leaf blocks in layout order, recursing into organizer blocks.

    Walks the blocks tree depth-first using blocks_layout ordering.
    For organizer blocks (those with nested blocks in 'data' or directly),
    recurses into children without yielding the organizer itself.

    Args:
        blocks_container: A dict with 'blocks' and 'blocks_layout' keys,
            e.g. the content object's fields or a column/tab object.
    """
    blocks = blocks_container.get("blocks", {})
    layout = blocks_container.get("blocks_layout", {})
    ordered_ids = layout.get("items", [])

    # Fall back to dict keys if no layout ordering
    if not ordered_ids:
        ordered_ids = list(blocks.keys())

    for block_id in ordered_ids:
        block = blocks.get(block_id)
        if block is None:
            continue

        # Check if this is an organizer block with nested blocks in "data"
        # (e.g. columnsBlock, tabs_block)
        data = block.get("data")
        if isinstance(data, dict) and "blocks" in data:
            # Recurse into each child container in layout order
            child_blocks = data.get("blocks", {})
            child_layout = data.get("blocks_layout", {})
            child_ids = child_layout.get("items", list(child_blocks.keys()))
            for child_id in child_ids:
                child = child_blocks.get(child_id)
                if child is None:
                    continue
                # Each child might itself be a container (e.g. a tab or column
                # with its own blocks/blocks_layout)
                if "blocks" in child:
                    yield from _iter_blocks_ordered(child)
                else:
                    yield child
        elif "blocks" in block and block.get("@type") not in ("slate", "text"):
            # Direct nested blocks (not in "data"), e.g. some organizer
            # variants. Skip slate/text which use "blocks" for Draft.js data.
            yield from _iter_blocks_ordered(block)
        else:
            # Leaf block - yield it
            yield block
