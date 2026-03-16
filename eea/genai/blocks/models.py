"""Pydantic models for structured LLM output of block operations."""

from pydantic import BaseModel, Field


class BlockGenerationResult(BaseModel):
    """Result of LLM block generation (multiple blocks)."""

    blocks: list[dict] = Field(
        description=(
            "Ordered list of block objects. Each block is a complete JSON "
            "object with '@type' and all block-specific fields. For organizer "
            "blocks (columnsBlock, tabs_block), include nested blocks inside "
            "the 'data' field with their own 'blocks' and 'blocks_layout'."
        ),
    )


class SingleBlockGenerationResult(BaseModel):
    """Result of LLM single block generation."""

    block: dict = Field(
        description=(
            "A single complete block JSON object with '@type' and all "
            "block-specific fields."
        ),
    )


class BlockRewriteResult(BaseModel):
    """Result of LLM block rewriting (multiple blocks)."""

    blocks: dict = Field(
        description=(
            "Dict mapping block UUIDs to rewritten block data. "
            "Must preserve the same UUIDs as the input."
        ),
    )


class SingleBlockRewriteResult(BaseModel):
    """Result of LLM single block rewriting."""

    block: dict = Field(
        description=(
            "The rewritten block as a complete JSON object with '@type' "
            "and all block-specific fields. Preserve the exact JSON "
            "structure, only modify text content."
        ),
    )
