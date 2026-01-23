"""
Chapter service for business logic related to chapters.
"""
from typing import List, Tuple, Optional
import pandas as pd

from models import Chapter
from database import DatabaseManager


class ChapterService:
    """
    Service class for managing chapter-related business logic.
    """

    def __init__(self):
        """Initialize the chapter service."""
        self.db_manager = DatabaseManager()

    def create_chapter(
        self,
        chapter_name: str,
        num_questions: int,
        num_options: int,
        correct_answers: List[str]
    ) -> Tuple[bool, str]:
        """
        Create a new chapter.

        Args:
            chapter_name: Name of the chapter
            num_questions: Number of questions
            num_options: Number of options per question
            correct_answers: List of correct answers

        Returns:
            Tuple of (success, message)
        """
        try:
            chapter = Chapter(
                chapter_name=chapter_name,
                num_questions=num_questions,
                num_options=num_options,
                correct_answers=correct_answers
            )
            return self.db_manager.save_chapter(chapter)
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error creating chapter: {str(e)}"

    def get_all_chapters(self) -> pd.DataFrame:
        """
        Get all chapters.

        Returns:
            DataFrame containing all chapters
        """
        return self.db_manager.get_all_chapters()

    def get_chapter_by_name(self, chapter_name: str) -> Optional[Chapter]:
        """
        Get a chapter by name.

        Args:
            chapter_name: Name of the chapter

        Returns:
            Chapter instance or None
        """
        return self.db_manager.get_chapter_by_name(chapter_name)

    def get_chapter_names(self) -> List[str]:
        """
        Get list of all chapter names.

        Returns:
            List of chapter names
        """
        chapters_df = self.get_all_chapters()
        if chapters_df.empty:
            return []
        return chapters_df['chapter_name'].tolist()

    def validate_chapter_exists(self, chapter_name: str) -> bool:
        """
        Check if a chapter exists.

        Args:
            chapter_name: Name of the chapter

        Returns:
            True if chapter exists, False otherwise
        """
        return self.get_chapter_by_name(chapter_name) is not None
