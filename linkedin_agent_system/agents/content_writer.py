"""
Content Writer Agent - Generates LinkedIn posts based on style guide
"""
from utils.gemini_client import GeminiClient
from models.data_models import StyleGuide, ContentPiece
import json
import uuid


class ContentWriter:
    """
    Generates LinkedIn content based on the user's style guide.
    Focuses solely on writing, using patterns extracted by StyleAnalyzer.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize Content Writer

        Args:
            gemini_client: Gemini API client
        """
        self.client = gemini_client

    def write_post(self, topic: str, style_guide: StyleGuide,
                   additional_instructions: str = "") -> ContentPiece:
        """
        Write a LinkedIn post on a given topic using the style guide

        Args:
            topic: Topic or prompt for the post
            style_guide: User's style guide
            additional_instructions: Optional additional instructions

        Returns:
            Generated content piece
        """
        prompt = self._create_writing_prompt(topic, style_guide, additional_instructions)
        content = self.client.generate(prompt, temperature=0.8)

        # Create ContentPiece
        content_piece = ContentPiece(
            id=str(uuid.uuid4()),
            topic=topic,
            content=content.strip()
        )

        return content_piece

    def revise_post(self, original_content: ContentPiece,
                    review_feedback: str,
                    style_guide: StyleGuide) -> ContentPiece:
        """
        Revise a post based on reviewer feedback

        Args:
            original_content: Original content that was reviewed
            review_feedback: Feedback from Content Reviewer
            style_guide: User's style guide

        Returns:
            Revised content piece
        """
        prompt = self._create_revision_prompt(
            original_content, review_feedback, style_guide
        )
        revised = self.client.generate(prompt, temperature=0.8)

        # Create new ContentPiece with same ID but updated content
        revised_piece = ContentPiece(
            id=original_content.id,
            topic=original_content.topic,
            content=revised.strip()
        )

        return revised_piece

    def _create_writing_prompt(self, topic: str, style_guide: StyleGuide,
                               additional_instructions: str) -> str:
        """Create prompt for generating new content"""
        style_description = self._format_style_guide(style_guide)

        prompt = f"""You are a LinkedIn Content Writer. Write a LinkedIn post on the following topic using the provided style guide.

TOPIC:
{topic}

STYLE GUIDE:
{style_description}

ADDITIONAL INSTRUCTIONS:
{additional_instructions if additional_instructions else "None"}

REQUIREMENTS:
1. Match the tone and voice exactly as described in the style guide
2. Follow the structure patterns
3. Use common expressions naturally where appropriate
4. Avoid expressions listed in avoided_expressions
5. Match the typical sentence and paragraph lengths
6. Make it engaging and valuable for LinkedIn audience
7. DO NOT use hashtags unless the style guide explicitly shows they are commonly used

Write the LinkedIn post now. Provide ONLY the post content, no additional commentary or labels."""

        return prompt

    def _create_revision_prompt(self, original_content: ContentPiece,
                                review_feedback: str,
                                style_guide: StyleGuide) -> str:
        """Create prompt for revising content"""
        style_description = self._format_style_guide(style_guide)

        prompt = f"""You are a LinkedIn Content Writer. Revise the following LinkedIn post based on the reviewer's feedback.

ORIGINAL POST:
{original_content.content}

REVIEWER FEEDBACK:
{review_feedback}

STYLE GUIDE:
{style_description}

REQUIREMENTS:
1. Address all issues raised in the feedback
2. Maintain alignment with the style guide
3. Improve the weak areas while keeping the strengths
4. Keep the core message about "{original_content.topic}"

Write the REVISED post now. Provide ONLY the post content, no additional commentary or labels."""

        return prompt

    def _format_style_guide(self, style_guide: StyleGuide) -> str:
        """Format style guide for use in prompts"""
        sections = []

        # Tone patterns
        if style_guide.tone_patterns:
            sections.append("TONE:")
            for pattern in style_guide.tone_patterns:
                sections.append(f"  • {pattern.pattern}")
                if pattern.examples:
                    sections.append(f"    Examples: {', '.join(pattern.examples[:2])}")

        # Structure patterns
        if style_guide.structure_patterns:
            sections.append("\nSTRUCTURE:")
            for pattern in style_guide.structure_patterns:
                sections.append(f"  • {pattern.pattern}")

        # Common expressions
        if style_guide.common_expressions:
            sections.append("\nCOMMON EXPRESSIONS:")
            for expr in style_guide.common_expressions[:10]:
                sections.append(f"  • {expr}")

        # Avoided expressions
        if style_guide.avoided_expressions:
            sections.append("\nAVOIDED EXPRESSIONS:")
            for expr in style_guide.avoided_expressions:
                sections.append(f"  • {expr}")

        # Metrics
        sections.append(f"\nSENTENCE LENGTH: ~{style_guide.sentence_length_avg} words average")
        sections.append(f"PARAGRAPH LENGTH: ~{style_guide.paragraph_length_avg} sentences average")

        return "\n".join(sections)
