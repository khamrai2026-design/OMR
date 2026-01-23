"""
Helper utilities for common operations.
"""
from typing import List
from config import OPTION_LETTERS


class OptionHelper:
    """
    Helper class for managing answer options.
    """

    @staticmethod
    def get_option_letters(num_options: int) -> List[str]:
        """
        Get list of option letters based on number of options.

        Args:
            num_options: Number of options

        Returns:
            List of option letters (A, B, C, D, etc.)
        """
        if num_options <= 0 or num_options > len(OPTION_LETTERS):
            raise ValueError(
                f"Number of options must be between 1 and {len(OPTION_LETTERS)}")
        return OPTION_LETTERS[:num_options]

    @staticmethod
    def validate_answer(answer: str, num_options: int) -> bool:
        """
        Validate if an answer is valid for the given number of options.

        Args:
            answer: Answer to validate
            num_options: Number of options

        Returns:
            True if valid, False otherwise
        """
        valid_options = OptionHelper.get_option_letters(num_options)
        return answer in valid_options


class FilterHelper:
    """
    Helper class for filtering data.
    """

    @staticmethod
    def filter_comparison_data(df, filter_option: str):
        """
        Filter comparison DataFrame based on filter option.

        Args:
            df: DataFrame with 'IsCorrect' column
            filter_option: Filter option ('All', 'Correct', 'Incorrect')

        Returns:
            Filtered DataFrame
        """
        if filter_option == "Correct":
            return df[df['IsCorrect'] == True].copy()
        elif filter_option == "Incorrect":
            return df[df['IsCorrect'] == False].copy()
        else:
            return df.copy()
