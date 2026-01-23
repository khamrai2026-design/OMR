"""
Exam Page - React Design Suite
"""
import streamlit as st
from datetime import datetime
from typing import Tuple

from ui.base_ui import BaseUI
from services import ChapterService, AttemptService
from utils import OptionHelper, ExcelExporter, FilterHelper
from config import FILE_DATE_FORMAT


class ExamPageUI(BaseUI):
    """
    Sleek Exam Interface following React design principles.
    """

    def __init__(self, theme: str = "indigo"):
        super().__init__(theme=theme)
        self.chapter_service = ChapterService()
        self.attempt_service = AttemptService()

    def render(self):
        # Hero Section
        st.markdown("""
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); padding: 3rem; border-radius: 30px; margin-bottom: 3rem; color: white; position: relative; overflow: hidden; box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);">
            <div style="position: absolute; top: -10%; right: -5%; width: 300px; height: 300px; background: rgba(255,255,255,0.1); border-radius: 50%;"></div>
            <div style="position: absolute; bottom: 5%; left: 2%; width: 100px; height: 100px; background: rgba(255,255,255,0.05); border-radius: 50%;"></div>
            <div style="position: relative; z-index: 1;">
                <span style="background: rgba(255,255,255,0.2); padding: 5px 15px; border-radius: 50px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;">Smart Examination</span>
                <h1 style="color: white !important; font-size: 3.5rem; font-weight: 800; margin-top: 1rem; margin-bottom: 0.5rem; letter-spacing: -2px;">OMR Digital Suite</h1>
                <p style="font-size: 1.25rem; opacity: 0.9; font-weight: 500; max-width: 600px;">Experience the next generation of answer sheet evaluation. Instant results, deep analytics, and professional reports.</p>
                <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
                    <div style="background: white; color: #6366f1; padding: 10px 25px; border-radius: 12px; font-weight: 700;">Start Test ↓</div>
                    <div style="background: rgba(255,255,255,0.2); color: white; padding: 10px 25px; border-radius: 12px; font-weight: 700; border: 1px solid rgba(255,255,255,0.3);">Tutorials</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<h2 style="font-size: 1.8rem; margin: 0.5rem 0; color: var(--text-main);">Take a Test</h2>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p style="font-size: 0.95rem; color: var(--text-muted); margin: 0 0 1.5rem 0;">Identify your progress and sharpen your skills.</p>',
            unsafe_allow_html=True
        )

        chapters_df = self.chapter_service.get_all_chapters()
        if chapters_df.empty:
            self.render_alert(
                "No chapters found in the database. Please initialize a chapter first.", "warning")
            return

        # Student Profile Card
        self.open_card("Student Profile")
        col1, col2 = st.columns(2)
        with col1:
            student_name = st.text_input(
                "Full Name", value="Arin Khamrai", placeholder="Enter student name")
        with col2:
            chapter_name = st.selectbox(
                "Select Chapter", options=chapters_df['chapter_name'].tolist())
        self.close_card()

        if not chapter_name:
            return

        chapter = self.chapter_service.get_chapter_by_name(chapter_name)
        if not chapter:
            self.render_alert("Unable to fetch chapter details.", "danger")
            return

        # Attempt Context
        if student_name:
            attempt_count = self.attempt_service.get_attempt_count(
                chapter.id, student_name)
            st.markdown(
                f'<p style="color: var(--text-muted); font-size: 0.9rem; margin-top: -10px; margin-bottom: 20px; padding-left: 5px;">📍 Attempting <b>#{attempt_count + 1}</b> for this chapter</p>', unsafe_allow_html=True)

        # Answer Sheet Grid
        self.open_card(f"Answer Sheet — {chapter_name}")
        submitted_answers = self._render_grid_answer_sheet(chapter)

        st.markdown('<div style="margin-top: 2rem;"></div>',
                    unsafe_allow_html=True)

        if st.button("🚀 Submit Examination", use_container_width=True, type="primary"):
            self._process_submission(student_name, chapter, submitted_answers)
        self.close_card()

    def _render_grid_answer_sheet(self, chapter) -> list:
        option_letters = OptionHelper.get_option_letters(chapter.num_options)

        st.markdown(f'<div style="background: #f8fafc; padding: 10px; border-radius: 8px; margin-bottom: 20px; border: 1px dashed #cbd5e1; font-size: 0.85rem; color: #64748b;">'
                    f'ℹ️ Total Questions: <b>{chapter.num_questions}</b> | Available Options: <b>{", ".join(option_letters)}</b>'
                    f'</div>', unsafe_allow_html=True)

        submitted_answers = []
        # Use 3 columns for a more compact layout
        cols = st.columns(3)
        
        for i in range(chapter.num_questions):
            col_idx = i % 3  # Distribute questions across 3 columns
            with cols[col_idx]:
                ans = st.radio(
                    f"Question {i+1}",
                    options=option_letters,
                    horizontal=True,
                    index=None,
                    key=f"ans_react_{i}"
                )
                submitted_answers.append((i, ans))

        submitted_answers.sort(key=lambda x: x[0])
        return [ans for idx, ans in submitted_answers]

    def _process_submission(self, student_name, chapter, submitted_answers):
        success, attempt, message = self.attempt_service.submit_attempt(
            chapter, student_name, submitted_answers
        )

        if not success:
            st.error(f"Error: {message}")
            return

        st.balloons()
        self.render_alert(
            "Test submitted successfully! View your performance below.", "success")

        # Display Results Inline
        st.markdown('<div style="margin-top: 2rem;"></div>',
                    unsafe_allow_html=True)
        self.render_header("Performance Summary")

        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            self.render_metric_card(
                f"{attempt.score}/{attempt.total_questions}", "Total Score")
        with m_col2:
            self.render_metric_card(
                f"{attempt.calculate_percentage():.1f}%", "Percentage")
        with m_col3:
            self.render_metric_card(str(attempt.attempt_number), "Attempt No.")

        # Detailed Comparison
        st.markdown('<div style="margin-top: 2rem;"></div>',
                    unsafe_allow_html=True)
        self.open_card("Answer Key Comparison")

        df_comp = self.attempt_service.get_answer_comparison(
            submitted_answers, chapter.correct_answers)

        fl_col1, fl_col2 = st.columns([0.8, 2])
        with fl_col1:
            st.markdown(
                '<p style="margin-top: 5px; font-weight: 600;">Filter Status:</p>', unsafe_allow_html=True)
        with fl_col2:
            f_opt = st.radio("Filter Status", [
                             "All", "Correct", "Incorrect"], horizontal=True, key="res_f", label_visibility="collapsed")

        df_filtered = FilterHelper.filter_comparison_data(df_comp, f_opt)

        # HTML Table for custom styling
        html_rows = ""
        for _, row in df_filtered.iterrows():
            status_class = "status-success" if row['Status'] == '✅' else "status-error"
            row_html = f"""
            <tr>
                <td><b>Q{row['Question']}</b></td>
                <td><span class="badge bg-secondary">{row['Your Answer'] or 'Empty'}</span></td>
                <td><span class="badge bg-primary">{row['Correct Answer']}</span></td>
                <td><span class="status-badge {status_class}">{row['Status']}</span></td>
            </tr>
            """
            html_rows += row_html

        st.markdown(f"""
        <table class="modern-table">
            <thead>
                <tr>
                    <th>Question</th>
                    <th>Your Ans</th>
                    <th>Correct Ans</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {html_rows}
            </tbody>
        </table>
        """, unsafe_allow_html=True)

        # Download Section
        st.markdown('<div style="margin-top: 1.5rem;"></div>',
                    unsafe_allow_html=True)
        excel_data = ExcelExporter.create_exam_report(
            student_name=student_name,
            chapter_name=chapter.chapter_name,
            score=attempt.score,
            total_questions=attempt.total_questions,
            percentage=attempt.calculate_percentage(),
            attempt_number=attempt.attempt_number,
            submitted_answers=submitted_answers,
            correct_answers=chapter.correct_answers,
            submitted_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        st.download_button(
            label="📄 Generate & Download Detailed PDF/Excel Report",
            data=excel_data,
            file_name=f"{student_name}_{chapter.chapter_name}_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        self.close_card()
