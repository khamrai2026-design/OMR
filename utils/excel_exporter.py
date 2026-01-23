"""
Excel export utilities for generating reports.
"""
from typing import List
from io import BytesIO
from datetime import datetime
import pandas as pd

from config import EXCEL_ENGINE, PRIMARY_COLOR


class ExcelExporter:
    """
    Utility class for exporting data to Excel format.
    """

    @staticmethod
    def create_exam_report(
        student_name: str,
        chapter_name: str,
        score: int,
        total_questions: int,
        percentage: float,
        attempt_number: int,
        submitted_answers: List[str],
        correct_answers: List[str],
        submitted_at: str = None
    ) -> bytes:
        """
        Create a comprehensive Excel report for an exam attempt.

        Args:
            student_name: Name of the student
            chapter_name: Name of the chapter
            score: Score achieved
            total_questions: Total number of questions
            percentage: Percentage score
            attempt_number: Attempt number
            submitted_answers: List of submitted answers
            correct_answers: List of correct answers
            submitted_at: Timestamp of submission

        Returns:
            Excel file as bytes
        """
        output = BytesIO()

        with pd.ExcelWriter(output, engine=EXCEL_ENGINE) as writer:
            workbook = writer.book

            # Define formats
            formats = ExcelExporter._create_formats(workbook)

            # Create sheets
            ExcelExporter._create_summary_sheet(
                writer, formats, student_name, chapter_name, score,
                total_questions, percentage, attempt_number, submitted_at
            )

            ExcelExporter._create_comparison_sheet(
                writer, formats, submitted_answers, correct_answers
            )

            ExcelExporter._create_analysis_sheet(
                writer, formats, score, total_questions, percentage, submitted_answers
            )

            ExcelExporter._create_detail_sheet(
                writer, formats, submitted_answers, correct_answers
            )

        return output.getvalue()

    @staticmethod
    def _create_formats(workbook):
        """Create Excel cell formats."""
        return {
            'header': workbook.add_format({
                'bold': True,
                'bg_color': PRIMARY_COLOR,
                'font_color': 'white',
                'border': 1,
                'align': 'center',
                'valign': 'vcenter'
            }),
            'correct': workbook.add_format({
                'bg_color': '#d4edda',
                'border': 1
            }),
            'incorrect': workbook.add_format({
                'bg_color': '#f8d7da',
                'border': 1
            }),
            'summary': workbook.add_format({
                'bold': True,
                'border': 1
            }),
            'cell': workbook.add_format({
                'border': 1,
                'align': 'center'
            })
        }

    @staticmethod
    def _create_summary_sheet(
        writer, formats, student_name, chapter_name, score,
        total_questions, percentage, attempt_number, submitted_at
    ):
        """Create exam summary sheet."""
        summary_data = {
            'Field': [
                'Student Name',
                'Chapter Name',
                'Date & Time',
                'Score',
                'Total Questions',
                'Percentage',
                'Attempt Number'
            ],
            'Value': [
                student_name,
                chapter_name,
                submitted_at if submitted_at else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                f"{score}/{total_questions}",
                total_questions,
                f"{percentage:.2f}%",
                attempt_number
            ]
        }

        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Exam Summary', index=False)

        summary_sheet = writer.sheets['Exam Summary']
        summary_sheet.set_column('A:A', 20)
        summary_sheet.set_column('B:B', 30)

        # Apply formatting
        for col_num, value in enumerate(summary_df.columns.values):
            summary_sheet.write(0, col_num, value, formats['header'])

        for row_num in range(1, len(summary_df) + 1):
            for col_num in range(len(summary_df.columns)):
                summary_sheet.write(
                    row_num, col_num,
                    summary_df.iloc[row_num-1, col_num],
                    formats['cell']
                )

    @staticmethod
    def _create_comparison_sheet(writer, formats, submitted_answers, correct_answers):
        """Create answer comparison sheet."""
        comparison_data = []
        for i in range(len(submitted_answers)):
            is_correct = submitted_answers[i] == correct_answers[i]
            comparison_data.append({
                'Question No.': i + 1,
                'Your Answer': submitted_answers[i] if submitted_answers[i] else 'Not Answered',
                'Correct Answer': correct_answers[i],
                'Status': 'Correct' if is_correct else 'Incorrect',
                'Remarks': '✓' if is_correct else '✗'
            })

        comparison_df = pd.DataFrame(comparison_data)
        comparison_df.to_excel(
            writer, sheet_name='Answer Comparison', index=False)

        comparison_sheet = writer.sheets['Answer Comparison']
        comparison_sheet.set_column('A:A', 15)
        comparison_sheet.set_column('B:B', 15)
        comparison_sheet.set_column('C:C', 15)
        comparison_sheet.set_column('D:D', 12)
        comparison_sheet.set_column('E:E', 10)

        # Apply formatting
        for col_num, value in enumerate(comparison_df.columns.values):
            comparison_sheet.write(0, col_num, value, formats['header'])

        for row_num in range(1, len(comparison_df) + 1):
            for col_num in range(len(comparison_df.columns)):
                cell_value = comparison_df.iloc[row_num-1, col_num]

                if col_num in [3, 4]:  # Status and Remarks columns
                    if cell_value in ['Correct', '✓']:
                        comparison_sheet.write(
                            row_num, col_num, cell_value, formats['correct'])
                    else:
                        comparison_sheet.write(
                            row_num, col_num, cell_value, formats['incorrect'])
                else:
                    comparison_sheet.write(
                        row_num, col_num, cell_value, formats['cell'])

    @staticmethod
    def _create_analysis_sheet(writer, formats, score, total_questions, percentage, submitted_answers):
        """Create performance analysis sheet."""
        analysis_data = {
            'Metric': [
                'Total Questions',
                'Correct Answers',
                'Incorrect Answers',
                'Not Answered',
                'Score',
                'Percentage',
                'Accuracy Rate'
            ],
            'Value': [
                total_questions,
                score,
                total_questions - score,
                sum(1 for ans in submitted_answers if ans is None),
                f"{score}/{total_questions}",
                f"{percentage:.2f}%",
                f"{(score/total_questions*100):.2f}%"
            ]
        }

        analysis_df = pd.DataFrame(analysis_data)
        analysis_df.to_excel(
            writer, sheet_name='Performance Analysis', index=False)

        analysis_sheet = writer.sheets['Performance Analysis']
        analysis_sheet.set_column('A:A', 25)
        analysis_sheet.set_column('B:B', 20)

        # Apply formatting
        for col_num, value in enumerate(analysis_df.columns.values):
            analysis_sheet.write(0, col_num, value, formats['header'])

        for row_num in range(1, len(analysis_df) + 1):
            for col_num in range(len(analysis_df.columns)):
                fmt = formats['summary'] if col_num == 0 else formats['cell']
                analysis_sheet.write(
                    row_num, col_num,
                    analysis_df.iloc[row_num-1, col_num],
                    fmt
                )

    @staticmethod
    def _create_detail_sheet(writer, formats, submitted_answers, correct_answers):
        """Create question-wise detail sheet."""
        detail_data = []
        for i in range(len(submitted_answers)):
            is_correct = submitted_answers[i] == correct_answers[i]
            detail_data.append({
                'Q.No': i + 1,
                'Your Answer': submitted_answers[i] if submitted_answers[i] else 'N/A',
                'Correct Answer': correct_answers[i],
                'Is Correct': 'Yes' if is_correct else 'No',
                'Points': 1 if is_correct else 0,
                'Feedback': 'Well done!' if is_correct else 'Review this topic'
            })

        detail_df = pd.DataFrame(detail_data)
        detail_df.to_excel(writer, sheet_name='Question Details', index=False)

        detail_sheet = writer.sheets['Question Details']
        detail_sheet.set_column('A:A', 8)
        detail_sheet.set_column('B:B', 12)
        detail_sheet.set_column('C:C', 12)
        detail_sheet.set_column('D:D', 10)
        detail_sheet.set_column('E:E', 8)
        detail_sheet.set_column('F:F', 25)

        # Apply formatting
        for col_num, value in enumerate(detail_df.columns.values):
            detail_sheet.write(0, col_num, value, formats['header'])

        for row_num in range(1, len(detail_df) + 1):
            for col_num in range(len(detail_df.columns)):
                cell_value = detail_df.iloc[row_num-1, col_num]

                if col_num in [3, 4]:  # Is Correct and Points columns
                    if cell_value in ['Yes', 1]:
                        detail_sheet.write(
                            row_num, col_num, cell_value, formats['correct'])
                    else:
                        detail_sheet.write(
                            row_num, col_num, cell_value, formats['incorrect'])
                else:
                    detail_sheet.write(
                        row_num, col_num, cell_value, formats['cell'])
