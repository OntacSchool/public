"""
Demo script for LinkedIn Agent System
Demonstrates the 4-agent workflow with sample data
"""
import os
import sys

# Add linkedin_agent_system to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'linkedin_agent_system'))

from linkedin_agent_system.main import LinkedInAgentSystem


def demo_workflow():
    """
    Demonstrate the complete workflow:
    1. Initialize with sample posts
    2. Generate new content
    3. Review process
    4. User feedback
    5. Learning and improvement
    """
    print("="*70)
    print("LINKEDIN AGENT SYSTEM - DEMO")
    print("="*70)

    # Check for API key
    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️  ERROR: GEMINI_API_KEY not found!")
        print("Please set your Gemini API key:")
        print("  export GEMINI_API_KEY='your-api-key'")
        print("\nGet a free key from: https://makersuite.google.com/app/apikey")
        return

    # Initialize system
    print("\n🚀 Initializing LinkedIn Agent System...")
    system = LinkedInAgentSystem()

    # Sample posts for initialization (these represent the user's writing style)
    sample_posts = [
        """I've been coding for 15 years. Here's what I wish I knew on day one:

Your code will be rewritten. That perfect function you spent hours on? Gone in 6 months. And that's okay.

The best engineers I know aren't the ones who write the cleverest code. They're the ones who make it easy for others to change.

Write for the person who comes after you. Including future you.""",

        """Three questions I ask before every code review:

1. Would I understand this in 6 months?
2. Could a junior dev modify it safely?
3. Is this the simplest solution that works?

If any answer is "no", I dig deeper.

Code review isn't about finding bugs. It's about building shared understanding.""",

        """Unpopular opinion: Your startup doesn't need microservices.

You need:
- Fast iteration
- Happy customers
- Revenue

Microservices give you:
- Distributed debugging
- Network latency
- Complex deployments

Start with a monolith. Scale when it hurts, not before."""
    ]

    # Initialize style guide with sample posts
    print("\n📚 STEP 1: Analyzing Your Writing Style")
    print("-" * 70)
    print("Processing sample posts to understand your style...")
    system.initialize_style_guide(sample_posts)

    # Generate a post
    print("\n✍️  STEP 2: Generating New Content")
    print("-" * 70)
    topic = "The importance of writing tests"
    print(f"Topic: {topic}")
    print("\nThis will go through the Writer → Reviewer loop automatically...")

    content = system.generate_post(topic)

    # Show the final result
    print("\n📄 FINAL POST (After Review):")
    print("="*70)
    print(content.content)
    print("="*70)
    print(f"\nScore: {content.score}/100")

    # Simulate user feedback - approval
    print("\n💬 STEP 3: Processing User Feedback")
    print("-" * 70)
    print("Simulating user approval with positive feedback...")

    system.process_user_feedback(
        content=content,
        feedback_text="Great! I like how this maintains the conversational tone and uses concrete examples.",
        approved=True
    )

    # Generate another post to show improvement
    print("\n✍️  STEP 4: Generating Another Post (System Should Be Improved)")
    print("-" * 70)
    topic2 = "Why documentation matters"
    print(f"Topic: {topic2}")

    content2 = system.generate_post(topic2)

    print("\n📄 SECOND POST:")
    print("="*70)
    print(content2.content)
    print("="*70)
    print(f"\nScore: {content2.score}/100")

    # Simulate rejection feedback
    print("\n💬 STEP 5: Processing Negative Feedback")
    print("-" * 70)
    print("Simulating user rejection with specific feedback...")

    system.process_user_feedback(
        content=content2,
        feedback_text="This is too formal. I prefer a more casual, personal tone. Also, avoid using 'leverage' - I never use that word.",
        approved=False
    )

    # Show statistics
    print("\n📊 STEP 6: System Statistics")
    print("-" * 70)
    stats = system.get_stats()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    # Show current style guide
    print("\n📖 STEP 7: Current Style Guide")
    print("-" * 70)
    system.show_style_guide()

    print("\n" + "="*70)
    print("DEMO COMPLETE!")
    print("="*70)
    print("\nWhat happened:")
    print("1. ✅ Style Analyzer learned your writing patterns from samples")
    print("2. ✅ Content Writer generated posts matching your style")
    print("3. ✅ Content Reviewer evaluated quality (with auto-revision)")
    print("4. ✅ Style Learner updated the guide based on your feedback")
    print("\nThe system is now smarter and will generate better content next time!")
    print("\nTry the interactive mode: cd linkedin_agent_system && python main.py")


def quick_demo():
    """
    Quick demo showing just the core functionality
    """
    print("="*70)
    print("QUICK DEMO - LinkedIn Agent System")
    print("="*70)

    if not os.getenv('GEMINI_API_KEY'):
        print("\n⚠️  Set GEMINI_API_KEY environment variable first!")
        return

    # Initialize
    system = LinkedInAgentSystem()

    # Quick sample
    samples = [
        "Quick tip: Always write tests. Future you will thank present you.",
        "Code review isn't optional. It's how teams build shared understanding.",
        "The best code is code you don't write. Solve the problem, not the puzzle."
    ]

    print("\nInitializing with sample posts...")
    system.initialize_style_guide(samples)

    print("\nGenerating post about 'pair programming'...")
    content = system.generate_post("Benefits of pair programming")

    print("\n" + "="*70)
    print("GENERATED POST:")
    print("="*70)
    print(content.content)
    print("="*70)

    print(f"\nScore: {content.score}/100")
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LinkedIn Agent System Demo")
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick demo (less verbose)'
    )

    args = parser.parse_args()

    if args.quick:
        quick_demo()
    else:
        demo_workflow()
