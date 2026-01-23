"""
UI package initialization.
"""
from .base_ui import BaseUI
from .exam_page import ExamPageUI
from .results_page import ResultsPageUI
from .analytics_page import AnalyticsPageUI

__all__ = ['BaseUI', 'ExamPageUI', 'ResultsPageUI', 'AnalyticsPageUI']
