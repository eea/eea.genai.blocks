"""REST API endpoint for LLM block generation."""

import json
import logging

from plone.restapi.services import Service

from eea.genai.blocks.generate import generate_block, generate_blocks

logger = logging.getLogger("eea.genai.blocks")


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

        # Single block mode if block_type is specified or single=true
        single = body.get("single", False) or "block_type" in body
        block_type = body.get("block_type")

        try:
            if single:
                return generate_block(
                    user_request, block_type=block_type,
                    context=self.context, request=self.request,
                )
            return generate_blocks(
                user_request, context=self.context,
                request=self.request,
            )
        except Exception as exc:
            logger.exception("Block generation failed")
            self.request.response.setStatus(500)
            return {"error": str(exc)}
