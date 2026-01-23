"""
Chapter model representing a test chapter.
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class Chapter:
    """
    Represents a test chapter with questions and correct answers.

    Attributes:
        id: Unique identifier for the chapter
        chapter_name: Name of the chapter
        num_questions: Number of questions in the chapter
        num_options: Number of options per question
        correct_answers: List of correct answers
        created_at: Timestamp when the chapter was created
    """
    chapter_name: str
    num_questions: int
    num_options: int
    correct_answers: List[str]
    id: Optional[int] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate chapter data after initialization."""
        if self.num_questions <= 0:
            raise ValueError("Number of questions must be positive")
        if self.num_options <= 0:
            raise ValueError("Number of options must be positive")
        if len(self.correct_answers) != self.num_questions:
            raise ValueError(
                "Number of correct answers must match number of questions")

    def to_dict(self) -> dict:
        """Convert chapter to dictionary."""
        return {
            'id': self.id,
            'chapter_name': self.chapter_name,
            'num_questions': self.num_questions,
            'num_options': self.num_options,
            'correct_answers': self.correct_answers,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def get_correct_answers_json(self) -> str:
        """Get correct answers as JSON string."""
        return json.dumps(self.correct_answers)

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Chapter':
        """
        Create a Chapter instance from a database row.

        Args:
            row: Database row tuple (id, chapter_name, num_questions, num_options, correct_answers_json, created_at)

        Returns:
            Chapter instance
        """
        id_, chapter_name, num_questions, num_options, correct_answers_json, created_at = row
        correct_answers = json.loads(correct_answers_json)

        return cls(
            id=id_,
            chapter_name=chapter_name,
            num_questions=num_questions,
            num_options=num_options,
            correct_answers=correct_answers,
            created_at=datetime.fromisoformat(
                created_at) if created_at else None
        )

    def __str__(self) -> str:
        """String representation of the chapter."""
        return f"Chapter(name={self.chapter_name}, questions={self.num_questions}, options={self.num_options})"
