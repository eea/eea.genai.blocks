"""REST API endpoint for LLM block rewriting."""

import json
import logging

from plone.restapi.services import Service

from eea.genai.blocks.rewrite import rewrite_block, rewrite_blocks

logger = logging.getLogger("eea.genai.blocks")


class LLMRewriteBlocksPost(Service):
    """POST @llm-rewrite-blocks

    Rewrite text content in existing Volto blocks using LLM.

    Multi-block request:
        {
            "blocks": {"uuid1": {...}, ...},
            "style": "more concise",
            "context": "optional page content for context"
        }

    Single-block request:
        {
            "block": {"@type": "slate", ...},
            "style": "more formal",
            "context": "optional page content for context"
        }

    If neither blocks nor block is provided, uses the context object's
    own blocks for multi-block rewriting.

    If "context" is omitted and the endpoint is called on a content
    object with blocks, the existing page text is extracted automatically.

    Multi-block response:
        {
            "blocks": {"uuid1": {...rewritten...}, ...}
        }

    Single-block response:
        {
            "block": {...rewritten...}
        }
    """

    def reply(self):
        body = json.loads(self.request.get("BODY", b"{}"))
        style = body.get("style")

        # Single block mode
        block = body.get("block")
        if block is not None:
            if not isinstance(block, dict) or "@type" not in block:
                self.request.response.setStatus(400)
                return {"error": "'block' must be a block object with '@type'"}
            try:
                return rewrite_block(
                    block, style=style, context=self.context,
                    request=self.request,
                )
            except Exception as exc:
                logger.exception("Single block rewriting failed")
                self.request.response.setStatus(500)
                return {"error": str(exc)}

        # Multi-block mode
        blocks = body.get("blocks")
        if blocks is None:
            blocks = getattr(self.context, "blocks", None) or {}

        if not blocks:
            self.request.response.setStatus(400)
            return {"error": "No blocks to rewrite"}

        try:
            return rewrite_blocks(
                blocks, style=style, context=self.context,
                request=self.request,
            )
        except Exception as exc:
            logger.exception("Block rewriting failed")
            self.request.response.setStatus(500)
            return {"error": str(exc)}
