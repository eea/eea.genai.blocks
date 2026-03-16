"""Block generation using agent system."""

import uuid as uuid_mod

from zope.component import queryUtility

from eea.genai.core.interfaces import IAgentExecutor
from eea.genai.core.agent import AgentDeps
from eea.genai.blocks.sanitizers import sanitize_block


def generate_blocks(user_request, page_context=None, context=None, request=None):
    """Generate Volto blocks from a natural language description using agents.

    Uses the ZCML-registered 'block_generator' agent (overridable via control panel).
    """
    executor = _get_agent_executor()

    result = executor.run_with_agent(
        "block_generator",
        user_prompt=user_request,
        deps=AgentDeps(context=context, request=request),
    )

    return _format_blocks_result(result)


def generate_block(user_request, block_type=None, page_context=None, context=None, request=None):
    """Generate a single Volto block using agents."""
    executor = _get_agent_executor()

    prompt = user_request
    if block_type:
        prompt = f"{user_request}\n\nBlock type: {block_type}"

    result = executor.run_with_agent(
        "block_generator_single",
        user_prompt=prompt,
        deps=AgentDeps(context=context, request=request),
    )

    block_data = result.block
    block_id = str(uuid_mod.uuid4())
    _ensure_uuids_in_block(block_data)
    return {
        "block_id": block_id,
        "block": sanitize_block(block_data),
    }


def _get_agent_executor():
    """Get the agent executor utility."""
    executor = queryUtility(IAgentExecutor)
    if executor is None:
        raise RuntimeError("No IAgentExecutor utility registered")
    return executor


def _format_blocks_result(result):
    """Convert BlockGenerationResult into blocks + blocks_layout."""
    blocks = {}
    layout_items = []

    for idx, block in enumerate(result.blocks):
        block_id = str(uuid_mod.uuid4())
        blocks[block_id] = block
        layout_items.append(block_id)
        _ensure_uuids_in_block(block)

    return {
        "blocks": blocks,
        "blocks_layout": {"items": layout_items},
    }


def _new_uuid():
    """Generate a new UUID4 string."""
    return str(uuid_mod.uuid4())


def _ensure_uuids_in_blocks_container(container):
    """Recursively replace all block IDs with proper UUID4s in a container.

    A container is a dict with 'blocks' (dict) and 'blocks_layout' (dict
    with 'items' list). This function:
    - Replaces each block key with a new UUID4
    - Updates blocks_layout.items to match
    - Recurses into organizer blocks (those with data.blocks or child blocks)
    """
    old_blocks = container.get("blocks", {})
    old_layout_items = container.get("blocks_layout", {}).get("items", [])

    # Build mapping from old IDs to new UUIDs
    id_map = {}
    for old_id in old_blocks:
        id_map[old_id] = _new_uuid()

    # Rebuild blocks dict with new UUIDs
    new_blocks = {}
    for old_id, block_data in old_blocks.items():
        new_id = id_map[old_id]

        # Recurse into organizer blocks
        data = block_data.get("data")
        if isinstance(data, dict) and "blocks" in data:
            _ensure_uuids_in_blocks_container(data)

        # Also handle direct nested blocks (e.g. tab objects with blocks)
        if "blocks" in block_data and isinstance(block_data["blocks"], dict):
            _ensure_uuids_in_blocks_container(block_data)

        new_blocks[new_id] = block_data

    container["blocks"] = new_blocks

    # Rebuild layout with new UUIDs (preserving order)
    if old_layout_items:
        container["blocks_layout"] = {
            "items": [id_map.get(old_id, old_id) for old_id in old_layout_items]
        }
    else:
        # No layout provided - use new blocks order
        container["blocks_layout"] = {"items": list(new_blocks.keys())}


def _ensure_uuids_in_block(block_data):
    """Ensure UUIDs in a single block's nested structures."""
    data = block_data.get("data")
    if isinstance(data, dict) and "blocks" in data:
        _ensure_uuids_in_blocks_container(data)

    if "blocks" in block_data and isinstance(block_data["blocks"], dict):
        _ensure_uuids_in_blocks_container(block_data)


# def _ensure_uuids_in_block(block):
#     """Replace placeholder IDs with UUIDs recursively."""
#     if not isinstance(block, dict):
#         return

#     # Handle blocks dict
#     if "blocks" in block and isinstance(block["blocks"], dict):
#         new_blocks = {}
#         for key, value in block["blocks"].items():
#             new_key = str(uuid_mod.uuid4())
#             new_blocks[new_key] = value
#             _ensure_uuids_in_block(value)
#         block["blocks"] = new_blocks

#     # Handle blocks_layout
#     if "blocks_layout" in block and isinstance(block["blocks_layout"], dict):
#         items = block["blocks_layout"].get("items", [])
#         block["blocks_layout"]["items"] = [str(uuid_mod.uuid4()) for _ in items]

#     # Recurse
#     for value in block.values():
#         if isinstance(value, dict):
#             _ensure_uuids_in_block(value)
#         elif isinstance(value, list):
#             for item in value:
#                 if isinstance(item, dict):
#                     _ensure_uuids_in_block(item)
#     blocks = {}
#     layout = []
#     for block_data in result.blocks:
#         block_id = _new_uuid()
#         _ensure_uuids_in_block(block_data)
#         blocks[block_id] = sanitize_block(block_data)
#         layout.append(block_id)

#     return {
#         "blocks": blocks,
#         "blocks_layout": {"items": layout},
#     }