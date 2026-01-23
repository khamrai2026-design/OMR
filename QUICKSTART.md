# Quick Start Guide

## 🚀 Getting Started with the  OMR System

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Installation

1. **Navigate to the project directory**
```bash
cd c:\Surajit\Python\OMR
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### Running the Application

**Option 1: New OOP Version (Recommended)**
```bash
streamlit run main.py
```

**Option 2: Legacy Version (For comparison)**
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### First Time Usage

1. **Navigate to "Exam" page** (default)
2. **Enter student name** (default: "Arin Khamrai")
3. **Select a chapter** (if chapters exist) or create one first
4. **Answer the questions** using radio buttons
5. **Submit the test** to see results
6. **Download Excel report** for detailed analysis

### Creating Your First Chapter

Since the database might be empty, you'll need to create a chapter programmatically or through the database:

**Method 1: Using Python Console**
```python
from services import ChapterService

service = ChapterService()
success, message = service.create_chapter(
    chapter_name="Sample Test",
    num_questions=5,
    num_options=4,
    correct_answers=['A', 'B', 'C', 'D', 'A']
)
print(message)
```

**Method 2: Direct Database Insert**
```python
from database import DatabaseManager
from models import Chapter

db = DatabaseManager()
chapter = Chapter(
    chapter_name="Mathematics Chapter 1",
    num_questions=10,
    num_options=4,
    correct_answers=['A', 'B', 'C', 'D', 'A', 'B', 'C', 'D', 'A', 'B']
)
success, message = db.save_chapter(chapter)
print(message)
```

### Testing the Installation

Run the test script to verify all imports work:
```bash
python test_imports.py
```

Expected output:
```
==================================================
OMR Application - Import and Functionality Test
==================================================
Testing imports...
✓ Config imported successfully
✓ Models imported successfully
✓ Database imported successfully
✓ Services imported successfully
✓ Utils imported successfully
✓ UI imported successfully

Testing basic functionality...
✓ DatabaseManager initialized
✓ Chapter created: Chapter(name=Test Chapter, questions=5, options=4)
✓ Option letters: ['A', 'B', 'C', 'D']

==================================================
✓ All tests passed!
==================================================
```

### Navigation

The application has three main pages:

#### 1. Exam Page
- Take tests
- Submit answers
- View immediate results
- Download reports

#### 2. View Results Page
- Filter by chapter and student
- See all attempts
- View detailed comparisons
- Export individual reports

#### 3. Analytics Page
- Overall statistics
- Chapter-wise performance
- Top performers leaderboard

### Understanding the Code

#### For Beginners
Start with these files in order:
1. `README.md` - Project overview
2. `REFACTOR_SUMMARY.md` - What changed and why
3. `models/chapter.py` - Simple data class
4. `models/attempt.py` - Another data class
5. `main.py` - Application entry point

#### For Intermediate
Explore the architecture:
1. `ARCHITECTURE.md` - Visual diagrams
2. `services/` - Business logic
3. `database/db_manager.py` - Database operations
4. `ui/base_ui.py` - UI base class

#### For Advanced
Deep dive into patterns:
1. `OOP_GUIDE.md` - Comprehensive OOP guide
2. All service classes - Business logic patterns
3. `utils/excel_exporter.py` - Complex Excel generation
4. Design pattern implementations

### Common Tasks

#### Adding a New Chapter
```python
from services import ChapterService

service = ChapterService()
service.create_chapter(
    chapter_name="Physics Chapter 1",
    num_questions=20,
    num_options=4,
    correct_answers=['A'] * 20  # Replace with actual answers
)
```

#### Viewing All Chapters
```python
from services import ChapterService

service = ChapterService()
chapters_df = service.get_all_chapters()
print(chapters_df)
```

#### Getting Analytics
```python
from services import AnalyticsService

service = AnalyticsService()
stats = service.get_overall_statistics()
print(stats)
```

### Troubleshooting

#### Issue: Module not found
**Solution**: Make sure you're in the correct directory
```bash
cd c:\Surajit\Python\OMR
python -c "import sys; print(sys.path)"
```

#### Issue: Database locked
**Solution**: Close any other connections to the database
```bash
# Stop the Streamlit app and restart
```

#### Issue: Import errors
**Solution**: Run the test script
```bash
python test_imports.py
```

### File Structure Quick Reference

```
OMR/
├── main.py              ← Start here (new version)
├── app.py               ← Legacy version
├── test_imports.py      ← Test imports
│
├── config/              ← Settings
├── models/              ← Data classes
├── database/            ← Database operations
├── services/            ← Business logic
├── utils/               ← Utilities
└── ui/                  ← User interface
```

### Next Steps

1. **Explore the code** - Start with `main.py`
2. **Read the guides** - `README.md`, `OOP_GUIDE.md`, `ARCHITECTURE.md`
3. **Run the app** - `streamlit run main.py`
4. **Create chapters** - Use the Python console
5. **Take tests** - Use the web interface
6. **View analytics** - Check the Analytics page

### Learning Path

**Day 1**: Understand the structure
- Read `REFACTOR_SUMMARY.md`
- Explore file organization
- Run `test_imports.py`

**Day 2**: Explore models and database
- Study `models/chapter.py`
- Study `models/attempt.py`
- Study `database/db_manager.py`

**Day 3**: Understand services
- Study `services/chapter_service.py`
- Study `services/attempt_service.py`
- Study `services/analytics_service.py`

**Day 4**: Explore UI
- Study `ui/base_ui.py`
- Study `ui/exam_page.py`
- Compare with legacy `app.py`

**Day 5**: Advanced concepts
- Read `OOP_GUIDE.md` thoroughly
- Study design patterns
- Understand SOLID principles

### Resources

- **Project Documentation**: All `.md` files in the root
- **Code Comments**: Docstrings in every file
- **Type Hints**: Throughout the codebase
- **Legacy Code**: `app.py` for comparison

### Support

For questions or issues:
1. Check the documentation files
2. Review the code comments
3. Compare with legacy `app.py`
4. Run `test_imports.py` for diagnostics

### Tips

✅ **Use type hints** - They help with IDE autocomplete
✅ **Read docstrings** - Every class and method is documented
✅ **Follow the layers** - UI → Services → Database → Models
✅ **Check examples** - `OOP_GUIDE.md` has many examples
✅ **Test frequently** - Run `test_imports.py` after changes

---

**Happy Coding! 🎉**

This refactored codebase is a professional example of OOP principles in Python. Use it to learn, extend, and build upon!
