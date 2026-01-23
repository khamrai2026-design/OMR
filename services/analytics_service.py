"""
Analytics service for generating statistics and reports.
"""
from typing import Dict, Any
import pandas as pd

from database import DatabaseManager


class AnalyticsService:
    """
    Service class for analytics and statistics.
    """

    def __init__(self):
        """Initialize the analytics service."""
        self.db_manager = DatabaseManager()

    def get_overall_statistics(self) -> Dict[str, Any]:
        """
        Get overall statistics across all chapters and attempts.

        Returns:
            Dictionary containing overall statistics
        """
        chapters_df = self.db_manager.get_all_chapters()
        attempts_df = self.db_manager.get_all_attempts()

        if attempts_df.empty:
            return {
                'total_chapters': len(chapters_df),
                'total_attempts': 0,
                'unique_students': 0,
                'overall_avg_percentage': 0.0
            }

        overall_avg = (attempts_df['score'] /
                       attempts_df['total_questions'] * 100).mean()

        return {
            'total_chapters': len(chapters_df),
            'total_attempts': len(attempts_df),
            'unique_students': attempts_df['student_name'].nunique(),
            'overall_avg_percentage': overall_avg
        }

    def get_chapter_statistics(self) -> pd.DataFrame:
        """
        Get statistics grouped by chapter.

        Returns:
            DataFrame with chapter-wise statistics
        """
        attempts_df = self.db_manager.get_all_attempts()

        if attempts_df.empty:
            return pd.DataFrame()

        chapter_stats = attempts_df.groupby('chapter_name').agg({
            'id': 'count',
            'score': 'mean',
            'total_questions': 'first',
            'student_name': 'nunique'
        }).reset_index()

        chapter_stats.columns = [
            'Chapter',
            'Total Attempts',
            'Avg Score',
            'Total Questions',
            'Unique Students'
        ]

        chapter_stats['Avg Percentage'] = (
            chapter_stats['Avg Score'] / chapter_stats['Total Questions'] * 100
        ).round(2)

        return chapter_stats

    def get_top_performers(self, limit: int = 10) -> pd.DataFrame:
        """
        Get top performing students.

        Args:
            limit: Number of top performers to return

        Returns:
            DataFrame with top performers
        """
        attempts_df = self.db_manager.get_all_attempts()

        if attempts_df.empty:
            return pd.DataFrame()

        student_stats = attempts_df.groupby('student_name').agg({
            'id': 'count',
            'score': 'sum',
            'total_questions': 'sum'
        }).reset_index()

        student_stats.columns = [
            'Student',
            'Total Attempts',
            'Total Score',
            'Total Questions'
        ]

        student_stats['Percentage'] = (
            student_stats['Total Score'] /
            student_stats['Total Questions'] * 100
        ).round(2)

        return student_stats.sort_values('Percentage', ascending=False).head(limit)

    def get_attempt_summary_statistics(self, chapter_name: str) -> Dict[str, Any]:
        """
        Get summary statistics for a specific chapter.

        Args:
            chapter_name: Name of the chapter

        Returns:
            Dictionary containing summary statistics
        """
        attempts_df = self.db_manager.get_student_attempts(chapter_name)

        if attempts_df.empty:
            return {
                'total_attempts': 0,
                'avg_score': 0.0,
                'avg_total': 0.0,
                'avg_percentage': 0.0,
                'unique_students': 0
            }

        return {
            'total_attempts': len(attempts_df),
            'avg_score': attempts_df['score'].mean(),
            'avg_total': attempts_df['total_questions'].mean(),
            'avg_percentage': (attempts_df['score'] / attempts_df['total_questions'] * 100).mean(),
            'unique_students': attempts_df['student_name'].nunique()
        }
