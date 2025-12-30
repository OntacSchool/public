"""
Style Learner Agent - Learns from user feedback to update style guide
"""
from utils.gemini_client import GeminiClient
from models.data_models import StyleGuide, FeedbackEntry, ContentPiece
import json


class StyleLearner:
    """
    Interprets user feedback and updates the style guide accordingly.
    Handles both approval and rejection feedback.
    Ensures the system continuously improves based on user preferences.
    """

    def __init__(self, gemini_client: GeminiClient):
        """
        Initialize Style Learner

        Args:
            gemini_client: Gemini API client
        """
        self.client = gemini_client

    def learn_from_feedback(self, content: ContentPiece,
                           feedback_entry: FeedbackEntry,
                           current_guide: StyleGuide) -> StyleGuide:
        """
        Update style guide based on user feedback

        Args:
            content: The content that received feedback
            feedback_entry: User's feedback
            current_guide: Current style guide

        Returns:
            Updated style guide
        """
        prompt = self._create_learning_prompt(content, feedback_entry, current_guide)
        response = self.client.generate(prompt, temperature=0.3)

        # Parse response into updated StyleGuide
        updated_guide = self._parse_learning_response(response)

        return updated_guide

    def extract_feedback_insights(self, feedback_text: str,
                                  content: ContentPiece) -> FeedbackEntry:
        """
        Extract structured insights from user's natural language feedback

        Args:
            feedback_text: User's feedback in natural language
            content: The content being reviewed

        Returns:
            Structured feedback entry
        """
        prompt = f"""You are a Feedback Analyzer. Analyze the user's feedback and extract key insights.

CONTENT:
{content.content}

USER FEEDBACK:
{feedback_text}

Analyze the feedback and provide a structured response in JSON format:
{{
    "feedback_type": "approval" or "rejection" or "modification",
    "specific_issues": ["issue 1", "issue 2", ...],
    "feedback_text": "summary of the feedback"
}}

If the user likes something, feedback_type is "approval".
If the user dislikes something or says "this isn't my style", feedback_type is "rejection".
If the user wants changes, feedback_type is "modification".

Extract specific issues mentioned (e.g., "too formal", "wrong tone", "too long", etc.)

Provide ONLY the JSON output, no additional text."""

        response = self.client.generate(prompt, temperature=0.3)

        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            data = json.loads(json_str)

            return FeedbackEntry(
                content_id=content.id,
                feedback_type=data.get('feedback_type', 'modification'),
                feedback_text=data.get('feedback_text', feedback_text),
                specific_issues=data.get('specific_issues', [])
            )
        except Exception as e:
            print(f"Error parsing feedback: {e}")
            # Return a basic feedback entry
            return FeedbackEntry(
                content_id=content.id,
                feedback_type='modification',
                feedback_text=feedback_text,
                specific_issues=[]
            )

    def _create_learning_prompt(self, content: ContentPiece,
                               feedback_entry: FeedbackEntry,
                               current_guide: StyleGuide) -> str:
        """Create prompt for learning from feedback"""
        return f"""You are a Style Learner. Update the style guide based on user feedback.

CURRENT STYLE GUIDE:
{json.dumps(current_guide.to_dict(), indent=2)}

CONTENT THAT RECEIVED FEEDBACK:
{content.content}

USER FEEDBACK:
Type: {feedback_entry.feedback_type}
Feedback: {feedback_entry.feedback_text}
Specific Issues: {', '.join(feedback_entry.specific_issues) if feedback_entry.specific_issues else 'None'}

INSTRUCTIONS:
1. If feedback_type is "approval":
   - Analyze what made this content good
   - Reinforce patterns used in this content
   - Add successful expressions to common_expressions

2. If feedback_type is "rejection":
   - Identify what the user disliked
   - Add problematic expressions to avoided_expressions
   - Update patterns to avoid similar issues

3. If feedback_type is "modification":
   - Understand what needs to change
   - Update relevant patterns
   - Add specific preferences to the guide

Update the style guide accordingly. Provide the updated guide in the same JSON format:
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

    def _parse_learning_response(self, response: str) -> StyleGuide:
        """
        Parse LLM response into updated StyleGuide

        Args:
            response: JSON response from LLM

        Returns:
            Updated StyleGuide object
        """
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]

            data = json.loads(json_str)

            # Import StylePattern here to avoid circular imports
            from models.data_models import StylePattern

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
            print(f"Error parsing learning response: {e}")
            print(f"Response: {response}")
            # Return unchanged guide on error
            return StyleGuide()

    def generate_learning_summary(self, old_guide: StyleGuide,
                                  new_guide: StyleGuide) -> str:
        """
        Generate summary of what was learned

        Args:
            old_guide: Previous style guide
            new_guide: Updated style guide

        Returns:
            Summary of changes
        """
        summary = "\n=== LEARNING UPDATE ===\n\n"

        # Check for new common expressions
        new_expressions = set(new_guide.common_expressions) - set(old_guide.common_expressions)
        if new_expressions:
            summary += "New preferred expressions added:\n"
            for expr in new_expressions:
                summary += f"  + {expr}\n"

        # Check for new avoided expressions
        new_avoided = set(new_guide.avoided_expressions) - set(old_guide.avoided_expressions)
        if new_avoided:
            summary += "\nNew expressions to avoid:\n"
            for expr in new_avoided:
                summary += f"  - {expr}\n"

        # Check for pattern changes
        if len(new_guide.tone_patterns) != len(old_guide.tone_patterns):
            summary += f"\nTone patterns updated: {len(old_guide.tone_patterns)} → {len(new_guide.tone_patterns)}\n"

        if len(new_guide.structure_patterns) != len(old_guide.structure_patterns):
            summary += f"Structure patterns updated: {len(old_guide.structure_patterns)} → {len(new_guide.structure_patterns)}\n"

        summary += "\nStyle guide has been updated and will be used for future content.\n"
        summary += "="*40 + "\n"

        return summary
