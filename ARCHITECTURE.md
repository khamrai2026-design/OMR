# Project Structure Diagram

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     OMR Application                          │
│                      (main.py)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │  Exam  │  │ Results │  │Analytics │
   │  Page  │  │  Page   │  │   Page   │
   └────┬───┘  └────┬────┘  └────┬─────┘
        │           │            │
        └───────────┼────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │    Service Layer      │
        ├───────────────────────┤
        │ • ChapterService      │
        │ • AttemptService      │
        │ • AnalyticsService    │
        └───────────┬───────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   ┌────────┐  ┌────────┐  ┌────────┐
   │ Models │  │Database│  │ Utils  │
   ├────────┤  ├────────┤  ├────────┤
   │Chapter │  │  DB    │  │ Excel  │
   │Attempt │  │Manager │  │Helpers │
   └────────┘  └────────┘  └────────┘
                    │
                    ▼
              ┌──────────┐
              │ SQLite   │
              │ Database │
              └──────────┘
```

## Layer Responsibilities

### Presentation Layer (UI)
```
ui/
├── base_ui.py          → Abstract base class
├── exam_page.py        → Exam interface
├── results_page.py     → Results viewing
└── analytics_page.py   → Analytics dashboard
```
**Responsibility**: User interaction and display

### Business Logic Layer (Services)
```
services/
├── chapter_service.py   → Chapter management
├── attempt_service.py   → Attempt processing
└── analytics_service.py → Statistics generation
```
**Responsibility**: Business rules and workflows

### Data Access Layer (Database)
```
database/
└── db_manager.py → Database operations (Singleton)
```
**Responsibility**: Data persistence and retrieval

### Domain Layer (Models)
```
models/
├── chapter.py → Chapter entity
└── attempt.py → Attempt entity
```
**Responsibility**: Data structure and validation

### Utility Layer (Utils)
```
utils/
├── excel_exporter.py → Report generation
└── helpers.py        → Helper functions
```
**Responsibility**: Reusable utilities

### Configuration Layer (Config)
```
config/
└── settings.py → Application settings
```
**Responsibility**: Centralized configuration

## Data Flow

### Exam Submission Flow
```
User Input (UI)
    ↓
ExamPageUI.render()
    ↓
AttemptService.submit_attempt()
    ↓
Attempt Model (validation)
    ↓
DatabaseManager.save_attempt()
    ↓
SQLite Database
    ↓
Success Response
    ↓
Display Results (UI)
```

### Results Viewing Flow
```
User Selection (UI)
    ↓
ResultsPageUI.render()
    ↓
AttemptService.get_student_attempts()
    ↓
DatabaseManager.get_student_attempts()
    ↓
SQLite Database
    ↓
DataFrame Response
    ↓
Display Table (UI)
```

### Analytics Flow
```
Page Load (UI)
    ↓
AnalyticsPageUI.render()
    ↓
AnalyticsService.get_overall_statistics()
    ↓
DatabaseManager.get_all_attempts()
    ↓
SQLite Database
    ↓
Aggregated Data
    ↓
Display Charts/Tables (UI)
```

## Class Relationships

### Inheritance Hierarchy
```
ABC (Python)
  ↓
BaseUI (Abstract)
  ├── ExamPageUI
  ├── ResultsPageUI
  └── AnalyticsPageUI
```

### Composition Relationships
```
OMRApplication
  ├── has-a → ExamPageUI
  ├── has-a → ResultsPageUI
  ├── has-a → AnalyticsPageUI
  └── has-a → DatabaseManager

ExamPageUI
  ├── has-a → ChapterService
  └── has-a → AttemptService

ChapterService
  └── has-a → DatabaseManager

AttemptService
  └── has-a → DatabaseManager

AnalyticsService
  └── has-a → DatabaseManager
```

### Dependency Graph
```
main.py
  └── depends on → ui/*
                    └── depends on → services/*
                                      └── depends on → database/*
                                      └── depends on → models/*
                                      └── depends on → utils/*
```

## Design Patterns Used

### 1. Singleton Pattern
```
DatabaseManager
  • Only one instance
  • Global access point
  • Shared state
```

### 2. Factory Pattern
```
Chapter.from_db_row()
Attempt.from_db_row()
  • Creates objects from data
  • Encapsulates creation logic
```

### 3. Template Method Pattern
```
BaseUI
  • setup_styles() - common
  • render() - abstract (template)
  
Subclasses implement render()
```

### 4. Context Manager Pattern
```
DatabaseManager.get_connection()
  • Automatic resource management
  • Exception safety
  • Transaction handling
```

## Module Dependencies

```
main.py
  ↓
ui/ → services/ → database/ → models/
  ↓       ↓
utils/  config/
```

**Dependency Rules:**
- UI depends on Services
- Services depend on Database and Models
- Database depends on Models
- Utils are independent
- Config is used by all

## File Organization

```
OMR/
│
├── main.py                 # Application entry point
├── app.py                  # Legacy code (reference)
├── test_imports.py         # Test script
├── README.md               # Project documentation
├── OOP_GUIDE.md           # OOP concepts guide
├── requirements.txt        # Dependencies
│
├── config/                 # Configuration
│   ├── __init__.py
│   └── settings.py
│
├── models/                 # Data models
│   ├── __init__.py
│   ├── chapter.py
│   └── attempt.py
│
├── database/              # Data access
│   ├── __init__.py
│   └── db_manager.py
│
├── services/              # Business logic
│   ├── __init__.py
│   ├── chapter_service.py
│   ├── attempt_service.py
│   └── analytics_service.py
│
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── excel_exporter.py
│   └── helpers.py
│
└── ui/                    # User interface
    ├── __init__.py
    ├── base_ui.py
    ├── exam_page.py
    ├── results_page.py
    └── analytics_page.py
```

## Key Concepts Summary

| Concept | Implementation | Location |
|---------|---------------|----------|
| Encapsulation | Private attributes, public methods | All classes |
| Inheritance | BaseUI → Page UIs | ui/ |
| Polymorphism | render() method override | ui/ |
| Abstraction | ABC, Service interfaces | ui/base_ui.py, services/ |
| Singleton | DatabaseManager | database/db_manager.py |
| Factory | from_db_row() | models/ |
| Template Method | BaseUI.render() | ui/base_ui.py |
| Context Manager | get_connection() | database/db_manager.py |

## Benefits Summary

✅ **Maintainability**: Clear separation of concerns
✅ **Testability**: Independent components
✅ **Reusability**: Shared functionality
✅ **Scalability**: Easy to extend
✅ **Readability**: Logical organization
✅ **Type Safety**: Type hints throughout
✅ **Error Handling**: Comprehensive validation
✅ **Documentation**: Docstrings for all classes/methods
