# OMR Sheet Submission System - OOP Refactored

A professional OMR (Optical Mark Recognition) sheet submission and evaluation system built with Python, Streamlit, and Object-Oriented Programming principles.

## 🏗️ Project Structure

```
OMR/
├── config/                 # Configuration settings
│   ├── __init__.py
│   └── settings.py        # Application constants and settings
│
├── models/                # Data models
│   ├── __init__.py
│   ├── chapter.py         # Chapter model with validation
│   └── attempt.py         # Attempt model with scoring logic
│
├── database/              # Database layer
│   ├── __init__.py
│   └── db_manager.py      # DatabaseManager (Singleton pattern)
│
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── chapter_service.py # Chapter management service
│   ├── attempt_service.py # Attempt submission service
│   └── analytics_service.py # Analytics and statistics service
│
├── utils/                 # Utility functions
│   ├── __init__.py
│   ├── excel_exporter.py  # Excel report generation
│   └── helpers.py         # Helper utilities
│
├── ui/                    # User interface components
│   ├── __init__.py
│   ├── base_ui.py         # Base UI class (Abstract)
│   ├── exam_page.py       # Exam taking page
│   ├── results_page.py    # Results viewing page
│   └── analytics_page.py  # Analytics dashboard page
│
├── main.py               # New main application entry point (OOP)
├── app.py                # Legacy application file (kept for reference)
├── omr_data.db           # SQLite database
└── requirements.txt      # Python dependencies
```

## 🎯 OOP Concepts Implemented

### 1. **Encapsulation**
- Data and methods are bundled together in classes
- Private attributes and methods (using `_` prefix)
- Public interfaces through well-defined methods

### 2. **Abstraction**
- `BaseUI` abstract class defines common UI interface
- Service layer abstracts business logic from UI
- Database operations abstracted through `DatabaseManager`

### 3. **Inheritance**
- All UI pages inherit from `BaseUI`
- Common functionality shared through inheritance
- Method overriding for specific page implementations

### 4. **Polymorphism**
- `render()` method implemented differently in each UI class
- Service methods work with different data types
- Flexible method signatures with optional parameters

### 5. **Design Patterns**

#### Singleton Pattern
- `DatabaseManager` ensures single database connection manager
- Prevents multiple instances and connection conflicts

#### Factory Pattern
- Model classes have `from_db_row()` class methods
- Creates objects from database rows

#### Template Method Pattern
- `BaseUI` provides template for UI rendering
- Subclasses implement specific rendering logic

#### Separation of Concerns
- **Models**: Data structure and validation
- **Database**: Data persistence
- **Services**: Business logic
- **UI**: Presentation layer
- **Utils**: Reusable utilities

## 🚀 Features

### Core Functionality
- ✅ Create and manage test chapters
- ✅ Submit OMR sheet answers
- ✅ Automatic scoring and evaluation
- ✅ Multiple attempts per student
- ✅ Answer comparison with filtering
- ✅ Excel report generation
- ✅ Analytics and statistics dashboard

### Technical Features
- ✅ SQLite database with proper schema
- ✅ Data validation at model level
- ✅ Context managers for safe database operations
- ✅ Type hints throughout the codebase
- ✅ Comprehensive error handling
- ✅ Bootstrap 5 styling
- ✅ Responsive design

## 📦 Installation

1. **Clone or navigate to the project directory**
```bash
cd c:\Surajit\Python\OMR
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Running the Application

**New OOP Version (Recommended):**
```bash
streamlit run main.py
```

**Legacy Version:**
```bash
streamlit run app.py
```

### Application Flow

1. **Exam Page**
   - Select or create a chapter
   - Enter student name
   - Answer questions using radio buttons
   - Submit and view results
   - Download Excel report

2. **View Results Page**
   - Filter by chapter and student
   - View summary statistics
   - See all attempts
   - View detailed answer comparison
   - Export individual reports

3. **Analytics Page**
   - Overall statistics
   - Chapter-wise performance
   - Top performers leaderboard

## 🔧 Configuration

Edit `config/settings.py` to customize:
- Database path
- Export directory
- UI colors and theme
- Date formats
- Number of option letters

## 📊 Database Schema

### Chapters Table
- `id`: Primary key
- `chapter_name`: Unique chapter name
- `num_questions`: Number of questions
- `num_options`: Options per question
- `correct_answers`: JSON array of correct answers
- `created_at`: Creation timestamp

### Attempts Table
- `id`: Primary key
- `chapter_id`: Foreign key to chapters
- `student_name`: Student name
- `submitted_answers`: JSON array of submitted answers
- `score`: Score achieved
- `total_questions`: Total questions
- `attempt_number`: Attempt number
- `submitted_at`: Submission timestamp

## 🎨 Code Quality

### Best Practices Followed
- ✅ PEP 8 style guide
- ✅ Type hints for better IDE support
- ✅ Docstrings for all classes and methods
- ✅ Error handling and validation
- ✅ DRY (Don't Repeat Yourself) principle
- ✅ Single Responsibility Principle
- ✅ Open/Closed Principle

### Class Responsibilities

**Models**: Data structure, validation, serialization
**Services**: Business logic, calculations, orchestration
**Database**: CRUD operations, transactions
**UI**: Rendering, user interaction
**Utils**: Reusable helper functions

## 🔄 Migration from Legacy Code

The original `app.py` has been refactored into:
- **Models**: `Chapter`, `Attempt`
- **Services**: `ChapterService`, `AttemptService`, `AnalyticsService`
- **Database**: `DatabaseManager`
- **UI**: `ExamPageUI`, `ResultsPageUI`, `AnalyticsPageUI`
- **Utils**: `ExcelExporter`, `OptionHelper`, `FilterHelper`

All functionality is preserved while improving:
- Code organization
- Maintainability
- Testability
- Reusability
- Scalability

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

Developed with ❤️ using Object-Oriented Programming principles.
