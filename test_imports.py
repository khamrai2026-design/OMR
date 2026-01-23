"""
Test script to verify all imports and basic functionality.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test all module imports."""
    print("Testing imports...")

    try:
        from config import settings
        print("✓ Config imported successfully")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        return False

    try:
        from models import Chapter, Attempt
        print("✓ Models imported successfully")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False

    try:
        from database import DatabaseManager
        print("✓ Database imported successfully")
    except Exception as e:
        print(f"✗ Database import failed: {e}")
        return False

    try:
        from services import ChapterService, AttemptService, AnalyticsService
        print("✓ Services imported successfully")
    except Exception as e:
        print(f"✗ Services import failed: {e}")
        return False

    try:
        from utils import ExcelExporter, OptionHelper, FilterHelper
        print("✓ Utils imported successfully")
    except Exception as e:
        print(f"✗ Utils import failed: {e}")
        return False

    try:
        from ui import ExamPageUI, ResultsPageUI, AnalyticsPageUI
        print("✓ UI imported successfully")
    except Exception as e:
        print(f"✗ UI import failed: {e}")
        return False

    return True


def test_basic_functionality():
    """Test basic functionality."""
    print("\nTesting basic functionality...")

    try:
        from database import DatabaseManager
        db = DatabaseManager()
        print("✓ DatabaseManager initialized")
    except Exception as e:
        print(f"✗ DatabaseManager initialization failed: {e}")
        return False

    try:
        from models import Chapter
        chapter = Chapter(
            chapter_name="Test Chapter",
            num_questions=5,
            num_options=4,
            correct_answers=['A', 'B', 'C', 'D', 'A']
        )
        print(f"✓ Chapter created: {chapter}")
    except Exception as e:
        print(f"✗ Chapter creation failed: {e}")
        return False

    try:
        from utils import OptionHelper
        options = OptionHelper.get_option_letters(4)
        print(f"✓ Option letters: {options}")
    except Exception as e:
        print(f"✗ OptionHelper failed: {e}")
        return False

    return True


if __name__ == "__main__":
    print("=" * 50)
    print("OMR Application - Import and Functionality Test")
    print("=" * 50)

    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()

    print("\n" + "=" * 50)
    if imports_ok and functionality_ok:
        print("✓ All tests passed!")
        print("=" * 50)
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        print("=" * 50)
        sys.exit(1)
