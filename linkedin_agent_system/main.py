"""
LinkedIn Agent System - Main Orchestrator
Coordinates the 4-agent workflow for LinkedIn content creation
"""
from agents import StyleAnalyzer, ContentWriter, ContentReviewer, StyleLearner
from utils import GeminiClient, DataStorage
from models import ContentPiece, FeedbackEntry
import config


class LinkedInAgentSystem:
    """
    Main orchestrator for the 4-agent LinkedIn content system.
    Manages the feedback loop: Writer → Reviewer → User → Learner → Analyzer
    """

    def __init__(self, api_key: str = None):
        """
        Initialize the agent system

        Args:
            api_key: Gemini API key (optional, uses env var if not provided)
        """
        # Initialize Gemini client
        self.gemini_client = GeminiClient(
            api_key=api_key or config.GEMINI_API_KEY,
            model=config.GEMINI_MODEL
        )

        # Initialize storage
        self.storage = DataStorage(config.DATA_DIR)

        # Initialize all 4 agents
        self.style_analyzer = StyleAnalyzer(self.gemini_client)
        self.content_writer = ContentWriter(self.gemini_client)
        self.content_reviewer = ContentReviewer(
            self.gemini_client,
            pass_threshold=config.REVIEWER_PASS_THRESHOLD
        )
        self.style_learner = StyleLearner(self.gemini_client)

        # Load existing data
        self.style_guide = self.storage.load_style_guide()
        self.feedback_logs = self.storage.load_feedback_logs()

        print("LinkedIn Agent System initialized successfully!")
        print(f"Style guide loaded: {len(self.style_guide.tone_patterns)} tone patterns")

    def initialize_style_guide(self, sample_posts: list[str]):
        """
        Initialize style guide by analyzing sample posts from the user

        Args:
            sample_posts: List of sample LinkedIn posts from the user
        """
        print("\n🔍 Analyzing your writing style...")

        # Convert to ContentPiece objects
        content_pieces = [
            ContentPiece(
                id=f"sample_{i}",
                topic="Sample",
                content=post,
                approved=True
            )
            for i, post in enumerate(sample_posts)
        ]

        # Analyze to create style guide
        self.style_guide = self.style_analyzer.analyze_content(content_pieces)

        # Save style guide
        self.storage.save_style_guide(self.style_guide)

        # Save sample posts as approved content
        for piece in content_pieces:
            self.storage.save_approved_content(piece)

        print("✅ Style guide created successfully!")
        print(self.style_analyzer.generate_style_summary(self.style_guide))

    def generate_post(self, topic: str, additional_instructions: str = "") -> ContentPiece:
        """
        Generate a LinkedIn post on a topic (with review loop)

        Args:
            topic: Topic for the post
            additional_instructions: Optional additional instructions

        Returns:
            Final content piece (may be revised)
        """
        print(f"\n✍️  Writing post about: {topic}")

        attempt = 0
        while attempt < config.MAX_REVISION_ATTEMPTS:
            attempt += 1

            # Writer generates content
            if attempt == 1:
                content = self.content_writer.write_post(
                    topic, self.style_guide, additional_instructions
                )
            else:
                # Revise based on previous review
                content = self.content_writer.revise_post(
                    content, review_result.detailed_feedback, self.style_guide
                )

            print(f"\n📝 Draft {attempt}:")
            print("-" * 60)
            print(content.content)
            print("-" * 60)

            # Reviewer evaluates content
            print(f"\n🔍 Reviewing draft {attempt}...")
            review_result = self.content_reviewer.review_content(
                content, self.style_guide, self.feedback_logs
            )

            print(self.content_reviewer.format_review_for_display(review_result))

            # If passed, return the content
            if review_result.passed:
                print(f"✅ Content passed review on attempt {attempt}!")
                content.score = review_result.score
                content.review_notes = review_result.detailed_feedback
                return content

            # If failed and still have attempts, revise
            if attempt < config.MAX_REVISION_ATTEMPTS:
                print(f"🔄 Revising... (Attempt {attempt + 1}/{config.MAX_REVISION_ATTEMPTS})")
            else:
                print(f"⚠️  Max revision attempts reached. Returning best attempt.")
                content.score = review_result.score
                content.review_notes = review_result.detailed_feedback
                return content

        return content

    def process_user_feedback(self, content: ContentPiece, feedback_text: str,
                             approved: bool = False):
        """
        Process user feedback and update the style guide

        Args:
            content: The content that received feedback
            feedback_text: User's feedback
            approved: Whether user approved the content
        """
        print("\n🧠 Learning from your feedback...")

        # Extract structured feedback
        if approved:
            feedback_entry = FeedbackEntry(
                content_id=content.id,
                feedback_type='approval',
                feedback_text=feedback_text or "Approved",
                specific_issues=[]
            )
        else:
            feedback_entry = self.style_learner.extract_feedback_insights(
                feedback_text, content
            )

        # Save feedback
        self.storage.save_feedback_entry(feedback_entry)
        self.feedback_logs.append(feedback_entry)

        # Update style guide based on feedback
        old_guide = self.style_guide
        self.style_guide = self.style_learner.learn_from_feedback(
            content, feedback_entry, self.style_guide
        )

        # Save updated style guide
        self.storage.save_style_guide(self.style_guide)

        # If approved, save to approved content and update analyzer
        if approved:
            content.approved = True
            content.feedback = feedback_text
            self.storage.save_approved_content(content)

            # Analyzer updates guide with new approved content
            self.style_guide = self.style_analyzer.update_style_guide(
                self.style_guide, content
            )
            self.storage.save_style_guide(self.style_guide)

        # Show learning summary
        print(self.style_learner.generate_learning_summary(old_guide, self.style_guide))

    def show_style_guide(self):
        """Display current style guide"""
        print(self.style_analyzer.generate_style_summary(self.style_guide))

    def get_stats(self) -> dict:
        """Get system statistics"""
        approved_content = self.storage.load_approved_content()

        return {
            'total_approved_posts': len(approved_content),
            'total_feedback_entries': len(self.feedback_logs),
            'tone_patterns': len(self.style_guide.tone_patterns),
            'structure_patterns': len(self.style_guide.structure_patterns),
            'common_expressions': len(self.style_guide.common_expressions),
            'avoided_expressions': len(self.style_guide.avoided_expressions)
        }


def main():
    """Main entry point for CLI usage"""
    import os

    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  GEMINI_API_KEY not found in environment variables!")
        print("Please set your Gemini API key:")
        print("  export GEMINI_API_KEY='your-api-key'")
        return

    # Initialize system
    system = LinkedInAgentSystem()

    # Check if style guide exists
    stats = system.get_stats()
    if stats['total_approved_posts'] == 0:
        print("\n👋 Welcome! Let's set up your style guide.")
        print("Please provide 3-5 sample LinkedIn posts you've written.")
        print("(Type 'DONE' when finished)\n")

        samples = []
        i = 1
        while True:
            print(f"\nSample Post {i}:")
            print("(Enter multiple lines, type 'DONE' on a new line to finish this post)")
            lines = []
            while True:
                line = input()
                if line.strip() == 'DONE':
                    break
                lines.append(line)

            post = '\n'.join(lines).strip()
            if post:
                samples.append(post)
                i += 1

            another = input("\nAdd another sample? (y/n): ").strip().lower()
            if another != 'y':
                break

        if samples:
            system.initialize_style_guide(samples)
        else:
            print("No samples provided. Using default style guide.")

    # Interactive loop
    print("\n" + "="*60)
    print("LinkedIn Agent System - Ready!")
    print("="*60)

    while True:
        print("\nOptions:")
        print("  1. Generate new post")
        print("  2. View style guide")
        print("  3. View statistics")
        print("  4. Exit")

        choice = input("\nChoice: ").strip()

        if choice == '1':
            topic = input("Topic: ").strip()
            if not topic:
                continue

            instructions = input("Additional instructions (optional): ").strip()

            content = system.generate_post(topic, instructions)

            print("\n" + "="*60)
            print("FINAL POST:")
            print("="*60)
            print(content.content)
            print("="*60)

            approve = input("\nApprove this post? (y/n): ").strip().lower()
            feedback_text = input("Any feedback? (optional): ").strip()

            system.process_user_feedback(content, feedback_text, approved=(approve == 'y'))

        elif choice == '2':
            system.show_style_guide()

        elif choice == '3':
            stats = system.get_stats()
            print("\n=== SYSTEM STATISTICS ===")
            for key, value in stats.items():
                print(f"{key.replace('_', ' ').title()}: {value}")

        elif choice == '4':
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
