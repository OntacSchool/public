"""
Style Analyzer Agent - Analyzes writing to extract style patterns
"""
from utils.gemini_client import GeminiClient
from models.data_models import StyleGuide, StylePattern, ContentPiece
from typing import List
import json


class StyleAnalyzer:
    """
    Analyzes user's writing to extract tone, structure, expressions, and patterns.
    Updates the style guide based on new approved content.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize Style Analyzer

        Args:
            gemini_client: Gemini API client
        """
        self.client = gemini_client

    def analyze_content(self, content_pieces: List[ContentPiece]) -> StyleGuide:
        """
        Analyze multiple content pieces to create a comprehensive style guide

        Args:
            content_pieces: List of approved content to analyze

        Returns:
            Complete style guide
        """
        if not content_pieces:
            return StyleGuide()

        # Prepare content for analysis
        content_texts = [piece.content for piece in content_pieces]
        combined_text = "\n\n---\n\n".join(content_texts)

        # Create analysis prompt
        prompt = self._create_analysis_prompt(combined_text)

        # Get analysis from LLM
        response = self.client.generate(prompt, temperature=0.3)

        # Parse response into StyleGuide
        style_guide = self._parse_analysis_response(response)

        return style_guide

    def update_style_guide(self, current_guide: StyleGuide,
                          new_content: ContentPiece) -> StyleGuide:
        """
        Update existing style guide with new approved content

        Args:
            current_guide: Current style guide
            new_content: New approved content to incorporate

        Returns:
            Updated style guide
        """
        prompt = self._create_update_prompt(current_guide, new_content)
        response = self.client.generate(prompt, temperature=0.3)
        updated_guide = self._parse_analysis_response(response)

        return updated_guide

    def _create_analysis_prompt(self, content: str) -> str:
        """Create prompt for analyzing content"""
        return f"""You are a Style Analyzer. Analyze the following LinkedIn posts to extract the author's writing style patterns.

Content to analyze:
{content}

Analyze and provide a detailed breakdown in the following JSON format:
{{
    "tone_patterns": [
        {{"category": "tone", "pattern": "description of tone pattern", "examples": ["example 1", "example 2"]}},
        ...
    ],
    "structure_patterns": [
        {{"category": "structure", "pattern": "description of structure pattern", "examples": ["example 1", "example 2"]}},
        ...
    ],
    "common_expressions": ["expression 1", "expression 2", ...],
    "avoided_expressions": [],
    "vocabulary_preferences": {{"formal_word": "preferred_informal_word", ...}},
    "sentence_length_avg": 15.0,
    "paragraph_length_avg": 3
}}

Focus on:
1. Tone: Is it conversational, professional, casual, authoritative, etc.?
2. Structure: How are posts organized? (storytelling, bullet points, questions, etc.)
3. Common expressions: Phrases or words frequently used
4. Sentence and paragraph patterns
5. Vocabulary preferences

Provide ONLY the JSON output, no additional text."""

    def _create_update_prompt(self, current_guide: StyleGuide,
                             new_content: ContentPiece) -> str:
        """Create prompt for updating style guide"""
        return f"""You are a Style Analyzer. Update the existing style guide by incorporating patterns from new approved content.

Current Style Guide:
{json.dumps(current_guide.to_dict(), indent=2)}

New Approved Content:
{new_content.content}

Update the style guide to incorporate new patterns while maintaining existing ones. If the new content reinforces existing patterns, increase their frequency. If it introduces new patterns, add them.

Provide the updated style guide in the same JSON format:
{{
    "tone_patterns": [...],
    "structure_patterns": [...],
    "common_expressions": [...],
    "avoided_expressions": [...],
    "vocabulary_preferences": {{...}},
    "sentence_length_avg": 15.0,
    "paragraph_length_avg": 3
}}

Provide ONLY the JSON output, no additional text."""

    def _parse_analysis_response(self, response: str) -> StyleGuide:
        """
        Parse LLM response into StyleGuide object

        Args:
            response: JSON response from LLM

        Returns:
            StyleGuide object
        """
        try:
            # Extract JSON from response (in case there's extra text)
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]

            data = json.loads(json_str)

            # Convert tone patterns
            tone_patterns = [
                StylePattern(**p) for p in data.get('tone_patterns', [])
            ]

            # Convert structure patterns
            structure_patterns = [
                StylePattern(**p) for p in data.get('structure_patterns', [])
            ]

            return StyleGuide(
                tone_patterns=tone_patterns,
                structure_patterns=structure_patterns,
                common_expressions=data.get('common_expressions', []),
                avoided_expressions=data.get('avoided_expressions', []),
                vocabulary_preferences=data.get('vocabulary_preferences', {}),
                sentence_length_avg=data.get('sentence_length_avg', 15.0),
                paragraph_length_avg=data.get('paragraph_length_avg', 3)
            )
        except Exception as e:
            print(f"Error parsing analysis response: {e}")
            print(f"Response: {response}")
            return StyleGuide()

    def generate_style_summary(self, style_guide: StyleGuide) -> str:
        """
        Generate human-readable summary of style guide

        Args:
            style_guide: Style guide to summarize

        Returns:
            Formatted summary
        """
        summary = "=== STYLE GUIDE SUMMARY ===\n\n"

        summary += "TONE PATTERNS:\n"
        for pattern in style_guide.tone_patterns:
            summary += f"  • {pattern.pattern}\n"
            if pattern.examples:
                summary += f"    Examples: {', '.join(pattern.examples[:2])}\n"

        summary += "\nSTRUCTURE PATTERNS:\n"
        for pattern in style_guide.structure_patterns:
            summary += f"  • {pattern.pattern}\n"

        summary += "\nCOMMON EXPRESSIONS:\n"
        for expr in style_guide.common_expressions[:5]:
            summary += f"  • {expr}\n"

        summary += f"\nAVERAGE SENTENCE LENGTH: {style_guide.sentence_length_avg} words\n"
        summary += f"AVERAGE PARAGRAPH LENGTH: {style_guide.paragraph_length_avg} sentences\n"

        return summary
