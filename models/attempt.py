"""
Attempt model representing a student's test attempt.
"""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import json


@dataclass
class Attempt:
    """
    Represents a student's attempt at a test.

    Attributes:
        chapter_id: ID of the chapter being attempted
        student_name: Name of the student
        submitted_answers: List of submitted answers
        score: Score achieved
        total_questions: Total number of questions
        attempt_number: Attempt number for this student and chapter
        id: Unique identifier for the attempt
        submitted_at: Timestamp when the attempt was submitted
    """
    chapter_id: int
    student_name: str
    submitted_answers: List[str]
    score: float
    total_questions: int
    attempt_number: int
    id: Optional[int] = None
    submitted_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate attempt data after initialization."""
        if self.score < 0 or self.score > self.total_questions:
            raise ValueError("Score must be between 0 and total questions")
        if self.attempt_number <= 0:
            raise ValueError("Attempt number must be positive")
        if len(self.submitted_answers) != self.total_questions:
            raise ValueError(
                "Number of submitted answers must match total questions")

    def calculate_percentage(self) -> float:
        """Calculate the percentage score."""
        if self.total_questions == 0:
            return 0.0
        return (self.score / self.total_questions) * 100

    def to_dict(self) -> dict:
        """Convert attempt to dictionary."""
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'student_name': self.student_name,
            'submitted_answers': self.submitted_answers,
            'score': self.score,
            'total_questions': self.total_questions,
            'attempt_number': self.attempt_number,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'percentage': self.calculate_percentage()
        }

    def get_submitted_answers_json(self) -> str:
        """Get submitted answers as JSON string."""
        return json.dumps(self.submitted_answers)

    @classmethod
    def from_db_row(cls, row: tuple) -> 'Attempt':
        """
        Create an Attempt instance from a database row.

        Args:
            row: Database row tuple

        Returns:
            Attempt instance
        """
        id_, chapter_id, student_name, submitted_answers_json, score, total_questions, attempt_number, submitted_at = row
        submitted_answers = json.loads(submitted_answers_json)

        return cls(
            id=id_,
            chapter_id=chapter_id,
            student_name=student_name,
            submitted_answers=submitted_answers,
            score=score,
            total_questions=total_questions,
            attempt_number=attempt_number,
            submitted_at=datetime.fromisoformat(
                submitted_at) if submitted_at else None
        )

    def __str__(self) -> str:
        """String representation of the attempt."""
        return f"Attempt(student={self.student_name}, score={self.score}/{self.total_questions}, attempt={self.attempt_number})"
