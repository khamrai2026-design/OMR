"""
Results Page - React Design Suite (Updated Layout)
"""
import streamlit as st
import json

from ui.base_ui import BaseUI
from services import ChapterService, AttemptService, AnalyticsService
from utils import ExcelExporter, FilterHelper


class ResultsPageUI(BaseUI):
    """
    Sleek Results interface for analyzing past attempts.
    Features a streamlined top-level selection for faster inspection.
    """

    def __init__(self, theme: str = "indigo"):
        super().__init__(theme=theme)
        self.chapter_service = ChapterService()
        self.attempt_service = AttemptService()
        self.analytics_service = AnalyticsService()

    def render(self):
        self.render_header(
            "Exam History", "Review and analyze student performance across chapters.")

        chapters_df = self.chapter_service.get_all_chapters()
        if chapters_df.empty:
            self.render_alert("No chapters available for review.", "warning")
            return

        # Filters Card - Consolidated
        self.open_card("Quick Selection")
        col1, col2 = st.columns(2)

        with col1:
            chapter_name = st.selectbox(
                "Select Chapter", options=chapters_df['chapter_name'].tolist(), key="results_chapter")

        if not chapter_name:
            self.close_card()
            return

        # Fetch all attempts for this chapter immediately
        attempts_df = self.attempt_service.get_student_attempts(chapter_name)

        with col2:
            if not attempts_df.empty:
                idx = st.selectbox(
                    "Select Attempt / Student",
                    options=range(len(attempts_df)),
                    format_func=lambda x: f"{attempts_df.iloc[x]['student_name']} — ver.{attempts_df.iloc[x]['attempt_number']}",
                    key="results_direct_inspect"
                )
            else:
                st.info("No records found.")
                idx = None
        self.close_card()

        if attempts_df.empty or idx is None:
            return

        # Aggregate Analytics for Chapter (Quick glance)
        self.render_header("Chapter Summary",
                           f"Collective metrics for {chapter_name}")
        stats = self.analytics_service.get_attempt_summary_statistics(
            chapter_name)

        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        with s_col1:
            self.render_metric_card(str(stats['total_attempts']), "Syncs")
        with s_col2:
            self.render_metric_card(f"{stats['avg_score']:.1f}", "Avg")
        with s_col3:
            self.render_metric_card(
                f"{stats['avg_percentage']:.1f}%", "Success")
        with s_col4:
            self.render_metric_card(str(stats['unique_students']), "Users")

        # Detailed Inspection of the SELECTED ATTEMPT
        st.markdown('<div style="margin-top: 2rem;"></div>',
                    unsafe_allow_html=True)
        selected_attempt = attempts_df.iloc[idx]
        self._render_detailed_inspection(selected_attempt, chapter_name)

    def _render_detailed_inspection(self, att, chapter_name):
        self.open_card(
            f"Inspection: {att['student_name']} (Attempt #{att['attempt_number']})")

        submitted_answers = json.loads(att['submitted_answers'])
        chapter = self.chapter_service.get_chapter_by_name(chapter_name)
        
        # Parse correct answers if it's a JSON string
        correct_answers = chapter.correct_answers
        if isinstance(correct_answers, str):
            try:
                correct_answers = json.loads(correct_answers)
            except (json.JSONDecodeError, TypeError):
                correct_answers = correct_answers

        st.markdown(
            f'<p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 20px;">🗓️ Submitted on: {att["submitted_at"]}</p>', unsafe_allow_html=True)

        fl_col1, fl_col2 = st.columns([0.8, 2])
        with fl_col1:
            st.markdown(
                '<p style="margin-top: 5px; font-weight: 600;">Status Filter:</p>', unsafe_allow_html=True)
        with fl_col2:
            f_opt = st.radio("Status Filter", ["All", "Correct", "Incorrect"],
                             horizontal=True, key=f"f_page_{att.name}", label_visibility="collapsed")

        df_comp = self.attempt_service.get_answer_comparison(
            submitted_answers, correct_answers)
        df_filtered = FilterHelper.filter_comparison_data(df_comp, f_opt)

        html_rows = ""
        for _, row in df_filtered.iterrows():
            status_class = "status-success" if row['Status'] == '✅' else "status-error"
            html_rows += f"""
            <tr>
                <td><b>Q{row['Question']}</b></td>
                <td><span class="badge bg-secondary">{row['Your Answer'] or 'Empty'}</span></td>
                <td><span class="badge bg-primary">{row['Correct Answer']}</span></td>
                <td><span class="status-badge {status_class}">{row['Status']}</span></td>
            </tr>
            """

        st.markdown(f"""
        <table class="modern-table">
            <thead>
                <tr><th>ID</th><th>Entry</th><th>Key</th><th>Status</th></tr>
            </thead>
            <tbody>{html_rows}</tbody>
        </table>
        """, unsafe_allow_html=True)

        # Action Bar
        st.markdown('<div style="margin-top: 1.5rem;"></div>',
                    unsafe_allow_html=True)
        excel_data = ExcelExporter.create_exam_report(
            student_name=att['student_name'],
            chapter_name=chapter_name,
            score=att['score'],
            total_questions=att['total_questions'],
            percentage=(att['score']/att['total_questions']*100),
            attempt_number=att['attempt_number'],
            submitted_answers=submitted_answers,
            correct_answers=correct_answers,
            submitted_at=att['submitted_at']
        )

        st.download_button(
            label=f"📥 Download Full Report for {att['student_name']}",
            data=excel_data,
            file_name=f"{att['student_name']}_{chapter_name}_v{att['attempt_number']}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        self.close_card()
