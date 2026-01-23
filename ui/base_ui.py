"""
Base UI component with a modern React-inspired design system.
Includes glassmorphism, vibrant gradients, and clean typography.
Supports multiple Bootstrap themes.
"""
import streamlit as st
from abc import ABC, abstractmethod
from utils.theme_manager import ThemeManager


class BaseUI(ABC):
    """
    Abstract base class for UI components with a professional React-style design.
    Supports multiple theme switching.
    """

    def __init__(self, theme: str = "indigo"):
        """
        Initialize the base UI component.
        
        Args:
            theme: Theme name from ThemeManager.THEMES
        """
        self.theme = theme
        self.setup_styles()

    def setup_styles(self):
        """Setup ultra-modern React-inspired CSS styles with selected theme."""
        theme_css = ThemeManager.get_theme_css(self.theme)
        st.markdown(theme_css, unsafe_allow_html=True)

    @abstractmethod
    def render(self):
        """Render the UI component. Must be implemented by subclasses."""
        pass

    def render_metric_card(self, value: str, label: str):
        """
        Render a premium metric card.
        """
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-val">{value}</div>
            <div class="metric-lbl">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    def render_alert(self, message: str, alert_type: str = "info"):
        """
        Render a clean modern alert.
        """
        icon = "💡"
        if alert_type == "success":
            icon = "✅"
        elif alert_type == "danger":
            icon = "🚨"
        elif alert_type == "warning":
            icon = "⚠️"

        st.markdown(f"""
        <div style="background: white; padding: 12px 16px; border-radius: 14px; border-left: 4px solid var(--primary); box-shadow: var(--shadow-sm); display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
            <span style="font-size: 1.2rem;">{icon}</span>
            <div style="color: var(--text-main); font-size: 0.9rem;">{message}</div>
        </div>
        """, unsafe_allow_html=True)

    def open_card(self, title: str = None):
        """Open a modern glass card."""
        header_html = f'<div class="card-header-v2">✨ {title}</div>' if title else ''
        st.markdown(
            f'<div class="glass-card">{header_html}', unsafe_allow_html=True)

    def close_card(self):
        """Close the glass card."""
        st.markdown('</div>', unsafe_allow_html=True)

    def render_header(self, title: str, subtitle: str = None):
        """Render a prominent page header."""
        subtitle_html = f'<p style="color: var(--text-muted); font-size: 1.1rem; margin-top: -8px; font-weight: 500;">{subtitle}</p>' if subtitle else ''
        st.markdown(f"""
        <div style="margin-bottom: 2.5rem; text-align: center;">
            <h1 style="color: var(--text-main); font-weight: 800; font-size: 3rem; letter-spacing: -0.04em; margin-bottom: 12px; background: linear-gradient(135deg, #0f172a 0%, #334155 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{title}</h1>
            {subtitle_html}
        </div>
        """, unsafe_allow_html=True)

    def render_footer(self):
        """Render a consistent website footer."""
        st.markdown("""
        <div class="footer-custom">
            <div style="margin-bottom: 1rem;">
                <span style="font-size: 1.5rem;">📝</span>
                <div style="font-weight: 800; color: var(--text-main); margin-top: 0.5rem;">OMR Pro Suite</div>
            </div>
            <p>© 2026 OMR Sheet Submission System. Built for Modern Educators.</p>
            <div style="display: flex; justify-content: center; gap: 1.5rem; margin-top: 1rem;">
                <span style="cursor: pointer; color: var(--primary);">Privacy Policy</span>
                <span style="cursor: pointer; color: var(--primary);">Terms of Service</span>
                <span style="cursor: pointer; color: var(--primary);">Support</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
