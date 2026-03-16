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
        block_types = get_block_types_description()
        if not block_types:
            return ""
        return f"Available block types:\n{block_types}"


def get_block_types_description():
    """Generate block types description from registered IBlockKnowledge.

    Use this to build the {block_types_description} part of the system prompt.
    """
    knowledge = dict(getUtilitiesFor(IBlockKnowledge))
    lines = []

    for name, kb in sorted(knowledge.items()):
        # Skip blocks that should not be included in generation
        if not getattr(kb, "include_in_generation", True):
            continue

        entry = f"- **{kb.title}** (@type: \"{name}\")"
        if kb.description:
            entry += f": {kb.description}"
        entry += f"\n  Schema: {kb.schema}"
        if kb.example:
            entry += f"\n  Example: {kb.example}"
        lines.append(entry)

        # Get additional context from this block type
        try:
            extra = kb.additional_prompt_context()
            if extra:
                lines.append(f"  Context: {extra}")
        except Exception:
            pass

    return "\n".join(lines)
