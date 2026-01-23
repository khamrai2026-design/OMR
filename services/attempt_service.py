"""
Attempt service for business logic related to student attempts.
"""
from typing import List, Optional, Tuple
import pandas as pd

from models import Attempt, Chapter
from database import DatabaseManager


class AttemptService:
    """
    Service class for managing attempt-related business logic.
    """

    def __init__(self):
        """Initialize the attempt service."""
        self.db_manager = DatabaseManager()

    def calculate_score(
        self,
        correct_answers: List[str],
        submitted_answers: List[str]
    ) -> int:
        """
        Calculate score based on correct and submitted answers.

        Args:
            correct_answers: List of correct answers
            submitted_answers: List of submitted answers

        Returns:
            Number of correct answers
        """
        return sum(1 for correct, submitted in zip(correct_answers, submitted_answers)
                   if correct == submitted)

    def submit_attempt(
        self,
        chapter: Chapter,
        student_name: str,
        submitted_answers: List[str]
    ) -> Tuple[bool, Optional[Attempt], str]:
        """
        Submit a student's attempt.

        Args:
            chapter: Chapter being attempted
            student_name: Name of the student
            submitted_answers: List of submitted answers

        Returns:
            Tuple of (success, attempt, message)
        """
        try:
            # Validate inputs
            if not student_name:
                return False, None, "Student name is required"

            if None in submitted_answers:
                return False, None, "Please answer all questions before submitting"

            # Calculate score
            score = self.calculate_score(
                chapter.correct_answers, submitted_answers)

            # Get attempt number
            attempt_number = self.db_manager.get_attempt_count(
                chapter.id, student_name
            ) + 1

            # Create attempt
            attempt = Attempt(
                chapter_id=chapter.id,
                student_name=student_name,
                submitted_answers=submitted_answers,
                score=score,
                total_questions=chapter.num_questions,
                attempt_number=attempt_number
            )

            # Save attempt
            success = self.db_manager.save_attempt(attempt)

            if success:
                return True, attempt, "Attempt submitted successfully!"
            else:
                return False, None, "Failed to save attempt"

        except ValueError as e:
            return False, None, str(e)
        except Exception as e:
            return False, None, f"Error submitting attempt: {str(e)}"

    def get_attempt_count(self, chapter_id: int, student_name: str) -> int:
        """
        Get the number of attempts for a student on a chapter.

        Args:
            chapter_id: ID of the chapter
            student_name: Name of the student

        Returns:
            Number of attempts
        """
        return self.db_manager.get_attempt_count(chapter_id, student_name)

    def get_student_attempts(
        self,
        chapter_name: str,
        student_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get attempts for a chapter, optionally filtered by student.

        Args:
            chapter_name: Name of the chapter
            student_name: Optional student name filter

        Returns:
            DataFrame containing attempts
        """
        return self.db_manager.get_student_attempts(chapter_name, student_name)

    def get_all_attempts(self) -> pd.DataFrame:
        """
        Get all attempts.

        Returns:
            DataFrame containing all attempts
        """
        return self.db_manager.get_all_attempts()

    def get_answer_comparison(
        self,
        submitted_answers: List[str],
        correct_answers: List[str]
    ) -> pd.DataFrame:
        """
        Create a comparison DataFrame of submitted vs correct answers.

        Args:
            submitted_answers: List of submitted answers
            correct_answers: List of correct answers

        Returns:
            DataFrame with answer comparison
        """
        comparison_data = []
        for i in range(len(submitted_answers)):
            is_correct = submitted_answers[i] == correct_answers[i]
            status_icon = "✅" if is_correct else "❌"
            comparison_data.append({
                "Question": f"Q.{i+1}",
                "Your Answer": submitted_answers[i] if submitted_answers[i] else 'Not Answered',
                "Correct Answer": correct_answers[i],
                "Status": status_icon,
                "IsCorrect": is_correct
            })

        return pd.DataFrame(comparison_data)
