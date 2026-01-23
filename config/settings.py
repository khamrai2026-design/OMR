"""
Configuration settings for the OMR application.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Database settings
DATABASE_NAME = 'omr_data.db'
DATABASE_PATH = BASE_DIR / DATABASE_NAME

# Export settings
EXPORT_DIR = BASE_DIR / 'exports'
EXPORT_DIR.mkdir(exist_ok=True)

# UI settings
PAGE_TITLE = "OMR System"
PAGE_ICON = "📝"
LAYOUT = "wide"

# Option letters
OPTION_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

# Streamlit theme colors (React-inspired Palette)
PRIMARY_COLOR = "#6366f1"  # Indigo
SUCCESS_COLOR = "#10b981"  # Emerald
DANGER_COLOR = "#ef4444"   # Red
WARNING_COLOR = "#f59e0b"  # Amber
INFO_COLOR = "#3b82f6"     # Blue
SECONDARY_COLOR = "#ec4899"  # Pink
ACCENT_COLOR = "#8b5cf6"    # Violet

# Excel export settings
EXCEL_ENGINE = 'xlsxwriter'

# Date format
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
FILE_DATE_FORMAT = "%Y%m%d_%H%M%S"
