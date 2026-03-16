"""REST API endpoint for LLM block generation."""

import json
import logging

from plone.restapi.services import Service

from eea.genai.blocks.generate import generate_block, generate_blocks
from eea.genai.blocks.context_providers import extract_text

logger = logging.getLogger("eea.genai.blocks")


def _get_page_context(context, body):
    """Extract page context from the request body or the content object.

    If "context" is provided in the request body, use that string directly.
    Otherwise, try to extract text from the content object's blocks
    using the extract_text utility.
    Also includes llm_summary if available on the content object.
    Returns None if no context is available.
    """
    explicit = body.get("context")
    if explicit:
        return explicit

    # Collect context parts from various sources
    context_parts = []

    # Extract text from blocks
    text = extract_text(context)
    if text:
        context_parts.append(text)

    # Get llm_summary if available on the content object
    llm_summary = getattr(context, "llm_summary", None)
    if llm_summary:
        context_parts.append(f"Existing summary:\n{llm_summary}")

    if context_parts:
        return "\n\n---\n\n".join(context_parts)

    return None


class LLMGenerateBlocksPost(Service):
    """POST @llm-generate-blocks

    Generate Volto blocks from a natural language description.

    Multi-block request:
        {
            "prompt": "Create a page about climate change...",
            "context": "optional page content for context"
        }

    Single-block request:
        {
            "prompt": "Write an introduction paragraph about...",
            "block_type": "slate",
            "context": "optional page content for context"
        }

    If "context" is omitted and the endpoint is called on a content
    object with blocks, the existing page text is extracted automatically.

    Multi-block response:
        {
            "blocks": {"uuid1": {...}, ...},
            "blocks_layout": {"items": ["uuid1", ...]}
        }

    Single-block response:
        {
            "block_id": "uuid",
            "block": {...}
        }
    """

    def reply(self):
        body = json.loads(self.request.get("BODY", b"{}"))
        user_request = body.get("prompt", "")

        if not user_request:
            self.request.response.setStatus(400)
            return {"error": "Missing 'prompt' in request body"}

        page_context = _get_page_context(self.context, body)

        # Single block mode if block_type is specified or single=true
        single = body.get("single", False) or "block_type" in body
        block_type = body.get("block_type")

        try:
            if single:
                return generate_block(
                    user_request, block_type=block_type,
                    page_context=page_context,
                    context=self.context, request=self.request,
                )
            return generate_blocks(
                user_request, page_context=page_context,
                context=self.context, request=self.request,
            )
        except Exception as exc:
            logger.exception("Block generation failed")
            self.request.response.setStatus(500)
            return {"error": str(exc)}
