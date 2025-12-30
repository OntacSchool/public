# LinkedIn Agent System

A multi-agent AI system for LinkedIn content creation that learns and improves from your feedback.

## 🌟 Overview

This system uses **4 specialized agents** working in a feedback loop to generate LinkedIn posts that match your unique writing style:

1. **Style Analyzer**: Analyzes your writing to extract tone, structure, expressions, and patterns
2. **Content Writer**: Generates posts based on your style guide
3. **Content Reviewer**: Objectively reviews generated content (requires 80+ score to pass)
4. **Style Learner**: Learns from your feedback to continuously improve

### The Feedback Loop

```
Writer → Reviewer → User → Learner → Analyzer (updates style guide) → Writer
```

Every time you provide feedback, the system gets better at matching your style.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Gemini API key (free from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd public
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your API key:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Or export it directly:
```bash
export GEMINI_API_KEY='your-api-key-here'
```

### First Run - Initialize Your Style Guide

On first run, the system will ask for 3-5 sample LinkedIn posts you've written. This helps the Style Analyzer understand your writing style.

```bash
cd linkedin_agent_system
python main.py
```

## 📖 Usage

### Interactive CLI

The main CLI provides these options:

1. **Generate new post**: Create a LinkedIn post on any topic
2. **View style guide**: See your current style patterns
3. **View statistics**: Check system stats
4. **Exit**: Close the system

### Programmatic Usage

```python
from linkedin_agent_system.main import LinkedInAgentSystem

# Initialize the system
system = LinkedInAgentSystem()

# If first time, initialize with sample posts
sample_posts = [
    "Your first sample post...",
    "Your second sample post...",
    "Your third sample post..."
]
system.initialize_style_guide(sample_posts)

# Generate a post
content = system.generate_post(
    topic="The importance of AI in modern software development",
    additional_instructions="Keep it under 200 words"
)

print(content.content)

# Provide feedback
system.process_user_feedback(
    content=content,
    feedback_text="Great! This matches my style perfectly",
    approved=True
)
```

## 🏗️ Architecture

```
linkedin_agent_system/
├── agents/
│   ├── style_analyzer.py    # Analyzes writing style
│   ├── content_writer.py    # Generates content
│   ├── content_reviewer.py  # Reviews content
│   └── style_learner.py     # Learns from feedback
├── models/
│   └── data_models.py       # Data structures
├── utils/
│   ├── gemini_client.py     # LLM integration
│   └── storage.py           # Data persistence
├── data/                    # Generated data files
│   ├── style_guide.json
│   ├── feedback_logs.json
│   └── approved_content.json
├── config.py                # Configuration
└── main.py                  # Main orchestrator
```

## 🔧 Configuration

Edit `config.py` to customize:

- `REVIEWER_PASS_THRESHOLD`: Minimum score to pass review (default: 80)
- `MAX_REVISION_ATTEMPTS`: Max revision attempts (default: 3)
- `GEMINI_MODEL`: Gemini model to use (default: "gemini-1.5-flash")

## 📊 How It Works

### 1. Style Analysis

The Style Analyzer examines your posts to identify:
- **Tone patterns**: Conversational, professional, casual, etc.
- **Structure patterns**: Storytelling, bullet points, questions, etc.
- **Common expressions**: Phrases you frequently use
- **Avoided expressions**: Patterns you don't use
- **Vocabulary preferences**: Word choices

### 2. Content Generation

The Writer creates posts using your style guide:
- Matches your tone exactly
- Follows your structural patterns
- Uses your common expressions
- Avoids what you don't like

### 3. Objective Review

The Reviewer scores content on:
- Tone alignment (25 points)
- Structure alignment (25 points)
- Expression usage (20 points)
- Writing quality (15 points)
- LinkedIn appropriateness (15 points)

Posts scoring below 80 are sent back for revision.

### 4. Continuous Learning

When you provide feedback:
- **Approval**: Patterns are reinforced, successful elements added to style guide
- **Rejection**: Problematic patterns added to avoid list
- **Modification**: Specific preferences updated

The system gets smarter with every interaction.

## 💡 Tips for Best Results

1. **Provide diverse samples**: Include different types of posts in your initial samples
2. **Be specific with feedback**: "Too formal" is better than "I don't like it"
3. **Approve good posts**: This helps reinforce what works
4. **Let it iterate**: The Reviewer will request revisions if needed
5. **Check your style guide**: View it periodically to see what the system has learned

## 🔐 Privacy & Data

All data is stored locally in the `data/` directory:
- `style_guide.json`: Your style patterns
- `feedback_logs.json`: Your feedback history
- `approved_content.json`: Posts you've approved

No data is sent anywhere except to Gemini API for processing.

## 🛠️ Troubleshooting

**Error: "GEMINI_API_KEY not found"**
- Make sure you've set the environment variable or created a `.env` file

**Posts don't match my style**
- Provide more sample posts during initialization
- Give specific feedback when posts are generated
- The system improves with more feedback

**Reviews are too strict/lenient**
- Adjust `REVIEWER_PASS_THRESHOLD` in `config.py`

## 📝 Example Workflow

```bash
# 1. Initialize system
python main.py

# 2. Provide 3-5 sample posts
# [System analyzes and creates style guide]

# 3. Generate a post
Topic: Benefits of code reviews
Additional instructions: Keep it short

# 4. Writer creates draft
# [Draft 1 shown]

# 5. Reviewer evaluates
# Score: 75/100 - FAILED
# Issues: Tone too formal, missing personal touch

# 6. Writer revises
# [Draft 2 shown]

# 7. Reviewer evaluates again
# Score: 85/100 - PASSED

# 8. You provide feedback
Approve: Yes
Feedback: Perfect! Love the conversational tone

# 9. System learns
# [Style guide updated with successful patterns]
```

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome!

## 📄 License

MIT License

## 🙏 Acknowledgments

Built using:
- Google Gemini API (free version)
- Python 3.8+

---

**Made with ❤️ for better LinkedIn content creation**
