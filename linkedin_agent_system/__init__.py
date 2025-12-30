"""
LinkedIn Agent System - Multi-agent AI for LinkedIn content creation

A system of 4 specialized agents working in a feedback loop:
- Style Analyzer: Analyzes writing to extract style patterns
- Content Writer: Generates posts based on style guide
- Content Reviewer: Objectively reviews generated content
- Style Learner: Learns from feedback to improve the system
"""

__version__ = "1.0.0"
__author__ = "LinkedIn Agent System"

from .main import LinkedInAgentSystem

__all__ = ['LinkedInAgentSystem']
