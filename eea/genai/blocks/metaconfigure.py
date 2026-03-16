"""Custom ZCML directives for eea.genai.core"""

from zope.component.zcml import utility
from zope.configuration import fields as configuration_fields
from zope.interface import Interface
from zope.schema import TextLine

from eea.genai.blocks.interfaces import IBlockKnowledge


# --- Agent block knowledge directive ---

class IBlockKnowledgeDirective(Interface):
    """Schema for the <genai:blockKnowledge> ZCML directive.

    Uses class-based knowledge: a class implementing IBlockKnowledge with
    all attributes (block_type, title, description, schema, example) and
    methods (text_extractor, block_sanitizer, additional_prompt_context).
    """

    block_type = TextLine(
        title="Block Type",
        description="The @type value of the block (e.g. 'slate', 'image')",
        required=True,
    )

    title = TextLine(
        title="Title",
        description="Human-readable name for this block type",
        required=True,
    )

    class_ = configuration_fields.GlobalObject(
        title="Class",
        description=(
            "A class implementing IBlockKnowledge with attributes and methods. "
            "All block knowledge (description, schema, example, text_extractor, "
            "block_sanitizer, additional_prompt_context) is defined in the class."
        ),
        required=True,
    )


def blockKnowledgeDirective(
    _context,
    block_type,
    title,
    class_,
):
    """Handler for <genai:blockKnowledge> ZCML directive.

    Registers a class-based IBlockKnowledge as a named utility
    so it can be looked up by block_type.
    """
    # Use class directly - it should implement IBlockKnowledge
    component = class_(block_type, title)
    utility(
        _context,
        provides=IBlockKnowledge,
        name=block_type,
        component=component,
    )
