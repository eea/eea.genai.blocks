"""Interfaces for eea.genai.blocks"""

from zope.interface import Attribute, Interface, implementer
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IGenAIBlocksLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


# Directive

class IBlockKnowledge(Interface):
    """Named utility holding knowledge about a Volto block type for LLM use.

    Registered with name=block_type (e.g. 'slate', 'image').

    All methods can be implemented as staticmethods in classes.
    """

    block_type = Attribute("The @type value of the block")
    title = Attribute("Human-readable name")
    description = Attribute("Description of the block for LLM context")
    schema = Attribute("JSON schema string describing the block structure")
    example = Attribute("JSON example string of a valid block")

    def text_extractor(block):
        """Extract plain text from a block of this type.

        Args:
            block: The block dict to extract text from.

        Returns:
            str: Plain text extracted from the block.
        """

    def block_sanitizer(block):
        """Sanitize a block after LLM generation/rewrite.

        Args:
            block: The block dict to sanitize.

        Returns:
            dict: Sanitized block dict.
        """

    def additional_prompt_context():
        """Return additional prompt text for this block type.

        Called when building prompts to include block-specific context
        (e.g., available images for image blocks).

        Returns:
            str: Additional prompt text, or empty string if no context.
        """


@implementer(IBlockKnowledge)
class BlockKnowledge:
    """Base class for block knowledge.

    Other Plone addons can inherit from this class to define block knowledge.

    Subclasses should define:
    - description: str - Description of the block for LLM context
    - schema: str - JSON schema string describing the block structure
    - example: str - JSON example string of a valid block
    - text_extractor(block): method - Extract plain text from a block (optional)
    - block_sanitizer(block): method - Sanitize a block after LLM generation (optional)
    - additional_prompt_context(): method - Return additional prompt text (optional)

    Usage::

        from eea.genai.blocks.interfaces import BlockKnowledge

        class MyBlockKnowledge(BlockKnowledge):
            description = "My custom block"
            schema = "{...}"
            example = "{...}"

            def additional_prompt_context(self):
                return "Custom context for my block"
    """

    description = ""
    schema = ""
    example = ""
    include_in_generation = True  # Set to False to exclude from generation prompts
    include_in_rewriting = True  # Set to False to exclude from rewriting prompts

    def __init__(self, block_type, title):
        self.block_type = block_type
        self.title = title

    def text_extractor(self, block):
        """Extract plain text from a block. Override in subclasses."""
        return ""

    def block_sanitizer(self, block):
        """Sanitize a block after LLM generation. Override in subclasses."""
        return block

    def additional_prompt_context(self):
        """Return additional prompt text. Override in subclasses."""
        return ""
