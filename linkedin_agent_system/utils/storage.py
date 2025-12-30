"""
Storage utilities for persisting data
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from models.data_models import StyleGuide, FeedbackEntry, ContentPiece


class DataStorage:
    """Handles data persistence for the agent system"""

    def __init__(self, data_dir: Path):
        """
        Initialize storage

        Args:
            data_dir: Directory for data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.style_guide_path = self.data_dir / "style_guide.json"
        self.feedback_logs_path = self.data_dir / "feedback_logs.json"
        self.approved_content_path = self.data_dir / "approved_content.json"

        # Initialize files if they don't exist
        self._initialize_files()

    def _initialize_files(self):
        """Create initial data files if they don't exist"""
        if not self.style_guide_path.exists():
            self.save_style_guide(StyleGuide())

        if not self.feedback_logs_path.exists():
            self._write_json(self.feedback_logs_path, [])

        if not self.approved_content_path.exists():
            self._write_json(self.approved_content_path, [])

    def _read_json(self, path: Path) -> Any:
        """Read JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {path}: {e}")
            return None

    def _write_json(self, path: Path, data: Any):
        """Write JSON file"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing {path}: {e}")

    def load_style_guide(self) -> StyleGuide:
        """Load style guide from storage"""
        data = self._read_json(self.style_guide_path)
        return StyleGuide.from_dict(data) if data else StyleGuide()

    def save_style_guide(self, style_guide: StyleGuide):
        """Save style guide to storage"""
        self._write_json(self.style_guide_path, style_guide.to_dict())

    def load_feedback_logs(self) -> List[FeedbackEntry]:
        """Load feedback logs from storage"""
        data = self._read_json(self.feedback_logs_path)
        if not data:
            return []
        return [FeedbackEntry.from_dict(entry) for entry in data]

    def save_feedback_entry(self, feedback: FeedbackEntry):
        """Add a new feedback entry"""
        logs = self.load_feedback_logs()
        logs.append(feedback)
        self._write_json(self.feedback_logs_path, [log.to_dict() for log in logs])

    def load_approved_content(self) -> List[ContentPiece]:
        """Load approved content from storage"""
        data = self._read_json(self.approved_content_path)
        if not data:
            return []
        return [ContentPiece.from_dict(item) for item in data]

    def save_approved_content(self, content: ContentPiece):
        """Add a new approved content piece"""
        approved = self.load_approved_content()
        approved.append(content)
        self._write_json(self.approved_content_path, [c.to_dict() for c in approved])

    def get_recent_approved_content(self, limit: int = 5) -> List[ContentPiece]:
        """Get most recent approved content"""
        approved = self.load_approved_content()
        return approved[-limit:] if len(approved) >= limit else approved
