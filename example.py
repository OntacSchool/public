"""
Simple example of using the LinkedIn Agent System
"""
import os
import sys

# Add linkedin_agent_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'linkedin_agent_system'))

from linkedin_agent_system.main import LinkedInAgentSystem


def main():
    # Initialize the system
    system = LinkedInAgentSystem()

    # Check if we need to initialize the style guide
    stats = system.get_stats()
    if stats['total_approved_posts'] == 0:
        print("No style guide found. Initializing with sample posts...\n")

        # Provide some sample posts that represent your writing style
        my_sample_posts = [
            """Your first sample LinkedIn post here.
This could be something you've actually posted before.""",

            """Your second sample post.
Try to provide 3-5 diverse examples of your writing.""",

            """Your third sample post.
The more examples, the better the system understands your style."""
        ]

        system.initialize_style_guide(my_sample_posts)

    # Generate a new post
    topic = "The value of continuous learning in tech"

    print(f"\nGenerating post about: {topic}\n")
    content = system.generate_post(
        topic=topic,
        additional_instructions="Keep it under 150 words and include a practical tip"
    )

    # Display the result
    print("\n" + "="*70)
    print("GENERATED POST:")
    print("="*70)
    print(content.content)
    print("="*70)
    print(f"\nReview Score: {content.score}/100\n")

    # In a real application, you'd ask the user for feedback
    # For this example, we'll simulate approval
    user_approved = True  # Change this based on actual user input
    user_feedback = "Great post! Matches my style well."

    if user_approved:
        system.process_user_feedback(
            content=content,
            feedback_text=user_feedback,
            approved=True
        )
        print("✅ Post approved and added to learning data!\n")
    else:
        system.process_user_feedback(
            content=content,
            feedback_text=user_feedback,
            approved=False
        )
        print("📝 Feedback recorded. System will learn from this.\n")

    # Show current statistics
    print("\nCurrent Statistics:")
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")


if __name__ == "__main__":
    if not os.getenv('GEMINI_API_KEY'):
        print("Error: GEMINI_API_KEY environment variable not set!")
        print("Please set it with: export GEMINI_API_KEY='your-key'")
        sys.exit(1)

    main()
