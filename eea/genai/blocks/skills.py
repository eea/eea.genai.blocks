"""Agent skills for eea.genai.blocks."""

from zope.component import getUtilitiesFor
from eea.genai.core.interfaces import AgentSkill
from eea.genai.blocks.interfaces import IBlockKnowledge


class BlocksKnowledgeSkill(AgentSkill):
    """Adds available block type descriptions to the system prompt.

    Discovers all registered IBlockKnowledge utilities and builds
    a formatted description of each block type's schema and examples.
    Use this skill for any agent that generates or works with Volto blocks.
    """

    name = "blocks_knowledge"
    description = "Adds available Volto block types to the system prompt"

    def system_prompt(self, deps):
        block_types = get_block_types_description() or ""
        # if not block_types:
        #     return ""
        # return f"Available block types:\n\n{block_types}"
        return block_types or ""


def get_block_types_description():
    """Generate block types description from registered IBlockKnowledge.

    Use this to build the {block_types_description} part of the system prompt.
    """
    knowledge = dict(getUtilitiesFor(IBlockKnowledge))
    lines = []

    k = 0
    for name, kb in sorted(knowledge.items()):
        # Skip blocks that should not be included in generation
        if not getattr(kb, "include_in_generation", True):
            continue

        if k > 0:
            entry = "\n\n"
        else:
            entry = ""

        entry += f"#### {kb.title} (@type: \"{name}\")"
        if kb.description:
            entry += f"\n\n{kb.description}"
        entry += f"\n\n**Schema:**\n\n{kb.schema}"
        if kb.example:
            entry += f"\n\n**Example:**\n\n{kb.example}"
        lines.append(entry)

        # Get additional context from this block type
        try:
            extra = kb.additional_prompt_context()
            if extra:
                lines.append(f"\n\n**Context:**\n\n{extra}")
        except Exception:
            pass

        k += 1

    return "\n".join(lines)
