"""
Main application entry point for the OMR Sheet Submission System.
React-inspired design architecture with multiple Bootstrap themes.
"""
import streamlit as st

from config import PAGE_TITLE, PAGE_ICON, LAYOUT
from database import DatabaseManager
from ui import ExamPageUI, ResultsPageUI, AnalyticsPageUI
from utils.theme_manager import ThemeManager


class OMRApplication:
    """
    Main application class for the OMR Sheet Submission System.
    Orchestrates the navigation and styling with theme support.
    """

    def __init__(self):
        """Initialize the OMR application."""
        self.db_manager = DatabaseManager()
        self.initialize_session_state()
        
        # Initialize UI pages with current theme
        theme = st.session_state.current_theme
        self.exam_page = ExamPageUI(theme=theme)
        self.results_page = ResultsPageUI(theme=theme)
        self.analytics_page = AnalyticsPageUI(theme=theme)

    def initialize_session_state(self):
        """Initialize Streamlit session state for theme persistence."""
        if "current_theme" not in st.session_state:
            st.session_state.current_theme = "indigo"

    def setup_page_config(self):
        """Configure the Streamlit page settings."""
        st.set_page_config(
            page_title=PAGE_TITLE,
            page_icon=PAGE_ICON,
            layout=LAYOUT
        )

    def render_theme_selector(self):
        """
        Render theme selector in the navbar area.
        """
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col3:
            themes = ThemeManager.get_available_themes()
            selected_theme = st.selectbox(
                "Select Theme:",
                themes,
                index=themes.index(st.session_state.current_theme) if st.session_state.current_theme in themes else 0,
                key="theme_selector"
            )
            
            # Update theme if changed
            if selected_theme != st.session_state.current_theme:
                st.session_state.current_theme = selected_theme
                st.rerun()

    def render_navbar(self):
        """
        Render a modern website-style top navigation bar.
        """
        # Render the custom CSS Navbar background and logo
        st.markdown(f"""
        <div class="navbar-custom">
            <div class="nav-logo">📝 OMR Pro</div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: #94a3b8; font-size: 0.8rem; font-family: 'Outfit';">v2.0 • Pro Suite</span>
                <div style="width: 32px; height: 32px; background: #f1f5f9; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.9rem;">👤</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Theme selector in sidebar area
        st.markdown('<div style="padding: 0 2rem; margin-bottom: 1.5rem;">', unsafe_allow_html=True)
        self.render_theme_selector()
        st.markdown('</div>', unsafe_allow_html=True)

        # Centered Navigation using Radio (styled as flat website tabs)
        st.markdown('<div class="nav-container">', unsafe_allow_html=True)
        menu = st.radio(
            "Navigation",
            ["Exam", "View Results", "Analytics"],
            key="main_nav",
            horizontal=True,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        return menu

    def run(self):
        """Run the application."""
        self.setup_page_config()
        menu = self.render_navbar()

        # Reinitialize UI pages with current theme
        theme = st.session_state.current_theme
        self.exam_page = ExamPageUI(theme=theme)
        self.results_page = ResultsPageUI(theme=theme)
        self.analytics_page = AnalyticsPageUI(theme=theme)

        if menu == "Exam":
            self.exam_page.render()
        elif menu == "View Results":
            self.results_page.render()
        elif menu == "Analytics":
            self.analytics_page.render()

        # Global Footer
        self.exam_page.render_footer()


def main():
    """Main entry point."""
    app = OMRApplication()
    app.run()


if __name__ == "__main__":
    main()

