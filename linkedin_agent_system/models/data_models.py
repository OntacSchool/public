"""
Data models for the LinkedIn Agent System
"""
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime
import json


@dataclass
class StylePattern:
    """Represents a style pattern extracted from user's writing"""
    category: str  # 'tone', 'structure', 'expression', 'vocabulary'
    pattern: str
    examples: List[str] = field(default_factory=list)
    frequency: int = 1

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class StyleGuide:
    """Complete style guide for the user"""
    tone_patterns: List[StylePattern] = field(default_factory=list)
    structure_patterns: List[StylePattern] = field(default_factory=list)
    common_expressions: List[str] = field(default_factory=list)
    avoided_expressions: List[str] = field(default_factory=list)
    vocabulary_preferences: Dict[str, str] = field(default_factory=dict)
    sentence_length_avg: float = 15.0
    paragraph_length_avg: int = 3
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            'tone_patterns': [p.to_dict() for p in self.tone_patterns],
            'structure_patterns': [p.to_dict() for p in self.structure_patterns],
            'common_expressions': self.common_expressions,
            'avoided_expressions': self.avoided_expressions,
            'vocabulary_preferences': self.vocabulary_preferences,
            'sentence_length_avg': self.sentence_length_avg,
            'paragraph_length_avg': self.paragraph_length_avg,
            'last_updated': self.last_updated
        }

    @classmethod
    def from_dict(cls, data):
        if not data:
            return cls()
        return cls(
            tone_patterns=[StylePattern.from_dict(p) for p in data.get('tone_patterns', [])],
            structure_patterns=[StylePattern.from_dict(p) for p in data.get('structure_patterns', [])],
            common_expressions=data.get('common_expressions', []),
            avoided_expressions=data.get('avoided_expressions', []),
            vocabulary_preferences=data.get('vocabulary_preferences', {}),
            sentence_length_avg=data.get('sentence_length_avg', 15.0),
            paragraph_length_avg=data.get('paragraph_length_avg', 3),
            last_updated=data.get('last_updated', datetime.now().isoformat())
        )


@dataclass
class FeedbackEntry:
    """User feedback on generated content"""
    content_id: str
    feedback_type: str  # 'approval', 'rejection', 'modification'
    feedback_text: str
    specific_issues: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class ContentPiece:
    """A piece of generated or approved content"""
    id: str
    topic: str
    content: str
    score: Optional[float] = None
    review_notes: str = ""
    approved: bool = False
    feedback: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


@dataclass
class ReviewResult:
    """Result of content review"""
    score: float
    passed: bool
    strengths: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    detailed_feedback: str = ""

    def to_dict(self):
        return asdict(self)
