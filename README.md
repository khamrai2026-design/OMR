# OMR Sheet Submission System

A comprehensive Streamlit application for managing OMR (Optical Mark Recognition) sheet submissions with database storage and analytics.

## Features

### 1. Create Chapter
- Define chapter name
- Set number of questions
- Set number of options per question
- Enter correct answer key using OMR-style radio buttons
- Store chapter configuration in database

### 2. Edit Chapter
- Modify chapter name
- Update answer key
- Delete chapters
- OMR-style radio button interface for easy editing

### 3. Submit OMR Sheet
- Select chapter
- Enter student name
- Fill in answers for all questions (using A, B, C, D format)
- Automatic scoring
- Support for multiple attempts per student per chapter
- View answer comparison after submission

### 3. View Results
- View results chapter-wise
- Filter by student name
- See all attempts with scores and percentages
- Detailed view of individual attempts
- Compare student answers with correct answers

### 4. Analytics Dashboard
- Overall statistics (total chapters, attempts, students)
- Chapter-wise performance metrics
- Top performers leaderboard
- Average scores and percentages

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. The app will open in your default web browser at `http://localhost:8501`

## Workflow

### For Teachers/Administrators:

1. **Create Chapter**:
   - Navigate to "Create Chapter" from the sidebar
   - Enter chapter name (e.g., "Chapter 1: Introduction to Physics")
   - Set number of questions and options
   - Enter the correct answer key
   - Click "Save Chapter"

2. **View Results**:
   - Navigate to "View Results"
   - Select a chapter
   - Optionally filter by student name
   - View detailed statistics and individual attempt details

3. **Analytics**:
   - Navigate to "Analytics" to see overall performance
   - View chapter-wise statistics
   - See top performers

### For Students:

1. **Submit OMR Sheet**:
   - Navigate to "Submit OMR Sheet"
   - Enter your name
   - Select the chapter
   - Fill in your answers
   - Click "Submit OMR Sheet"
   - View your score and answer comparison

2. **Multiple Attempts**:
   - You can submit multiple attempts for the same chapter
   - Each attempt is tracked separately
   - Attempt number is displayed before submission

## Database

The application uses SQLite database (`omr_data.db`) with two main tables:

### Chapters Table
- `id`: Primary key
- `chapter_name`: Unique chapter identifier
- `num_questions`: Number of questions
- `num_options`: Number of options per question
- `correct_answers`: JSON array of correct answers
- `created_at`: Timestamp

### Attempts Table
- `id`: Primary key
- `chapter_id`: Foreign key to chapters table
- `student_name`: Name of the student
- `submitted_answers`: JSON array of submitted answers
- `score`: Number of correct answers
- `total_questions`: Total number of questions
- `attempt_number`: Attempt number for this student-chapter combination
- `submitted_at`: Timestamp

## Features Highlights

✅ Multiple chapters support
✅ Configurable number of questions and options
✅ Multiple attempts per student per chapter
✅ Automatic scoring
✅ Answer comparison view
✅ Chapter-wise result filtering
✅ Student-wise result filtering
✅ Analytics dashboard
✅ SQLite database for persistent storage
✅ User-friendly interface
✅ Real-time statistics

## Technical Details

- **Framework**: Streamlit
- **Database**: SQLite3
- **Data Processing**: Pandas
- **Storage Format**: JSON for answer arrays

## Notes

- The database file (`omr_data.db`) will be created automatically in the same directory as the app
- All data is stored locally
- Chapter names must be unique
- Students can take unlimited attempts for any chapter
- Each attempt is tracked separately with attempt numbers

["C", "D", "D", "C", "A", "C", "B", "C", "B", "C", "D", "C", "B", "C", "D", "A", "D", "D", "B", "A"]
["A", "A", "B", "C", "A", "B", "C", "D", "B", "A", "B", "C", "C", "C", "A", "D", "C", "A", "C", "B"]
["B", "D", "B", "C", "A", "D", "B", "A", "B", "C", "D", "A", "C", "C", "D", "B", "C", "C", "B", "B"]
["D", "D", "C", "D", "D", "D", "D", "C", "D", "D", "B", "D", "A", "C", "C", "C", "D", "B", "A", "D"]
["A", "B", "B", "C", "D", "D", "D", "C", "A", "B", "D", "C", "C", "B", "C", "A", "B", "A", "A", "C"]
["C", "A", "B", "D", "A", "B", "A", "D", "B", "A", "D", "B", "C", "B", "D", "A", "C", "D", "A", "A"]




["1", "2", "3", "4", "5", "6", "7", "8", "9","10","11", "12","13","14","15","16","17","18","19","20"]
["D", "A", "B", "B", "D", "D", "D", "A", "B", "C", "D", "D", "A", "C", "D", "D", "D", "A", "C", "D"]