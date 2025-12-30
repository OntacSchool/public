"""
Configuration settings for the LinkedIn Agent System
"""
import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# Data files
STYLE_GUIDE_PATH = DATA_DIR / "style_guide.json"
FEEDBACK_LOGS_PATH = DATA_DIR / "feedback_logs.json"
APPROVED_CONTENT_PATH = DATA_DIR / "approved_content.json"

# Gemini API Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-1.5-flash"  # Free version

# Agent Configuration
REVIEWER_PASS_THRESHOLD = 80  # Minimum score to pass review
MAX_REVISION_ATTEMPTS = 3  # Maximum times Writer can revise

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)
