# Quick Start Guide - OMR Sheet Submission System

## Getting Started in 3 Steps

### Step 1: Run the Application
```bash
streamlit run app.py
```
The app will open at: http://localhost:8501

### Step 2: Create Your First Chapter
1. Click on **"Create Chapter"** in the sidebar
2. Fill in the details:
   - Chapter Name: "Sample Test - Mathematics"
   - Number of Questions: 5
   - Number of Options: 4
3. Enter the correct answers (e.g., 1, 2, 3, 4, 1)
4. Click **"Save Chapter"**

### Step 3: Submit Your First OMR Sheet
1. Click on **"Submit OMR Sheet"** in the sidebar
2. Enter your name: "John Doe"
3. Select chapter: "Sample Test - Mathematics"
4. Fill in your answers for all 5 questions
5. Click **"Submit OMR Sheet"**
6. View your score and answer comparison!

## Example Workflow

### Scenario: Teacher Creating a Quiz

**Chapter Details:**
- Chapter: "Physics - Chapter 1: Motion"
- Questions: 10
- Options: 4 (A, B, C, D)

**Answer Key:**
Q1: B, Q2: C, Q3: A, Q4: D, Q5: B, Q6: A, Q7: C, Q8: B, Q9: D, Q10: A

### Scenario: Student Taking the Test

**Student:** Alice
**Answers:** B, C, A, D, B, A, C, B, C, A

**Result:** 9/10 (90%) - Q9 is incorrect (answered C, correct answer is D)

### Scenario: Student Retaking the Test

**Student:** Alice (2nd Attempt)
**Answers:** B, C, A, D, B, A, C, B, D, A

**Result:** 10/10 (100%) - Perfect score!

## Features Demo

### Multiple Attempts
- Alice can take the test multiple times
- Each attempt is tracked separately
- Attempt numbers are automatically assigned

### View Results
- Filter by chapter: "Physics - Chapter 1: Motion"
- Filter by student: "Alice"
- See both attempts with scores and timestamps

### Analytics
- Overall statistics across all chapters
- Chapter-wise performance comparison
- Top performers leaderboard

## Tips

✅ **For Teachers:**
- Create chapters before students start submitting
- Use descriptive chapter names
- Double-check the answer key before saving
- Use "View Results" to monitor student performance
- Use "Analytics" to identify struggling students

✅ **For Students:**
- Make sure to enter your name correctly each time
- Select the correct chapter
- Review your answers before submitting
- Check the answer comparison after submission
- You can retake tests to improve your score

## Database Location

The database file `omr_data.db` is created in the same folder as `app.py`. This file contains:
- All chapter configurations
- All student attempts
- All scores and timestamps

**Backup Tip:** Regularly backup the `omr_data.db` file to prevent data loss!

## Troubleshooting

**Issue:** App won't start
**Solution:** Make sure you have installed the requirements:
```bash
pip install -r requirements.txt
```

**Issue:** Can't see my chapter
**Solution:** Make sure you clicked "Save Chapter" after entering the details

**Issue:** Wrong score calculation
**Solution:** Verify the answer key in the database by checking the "Existing Chapters" section

## Next Steps

1. ✅ Create multiple chapters for different subjects
2. ✅ Have students submit their OMR sheets
3. ✅ Monitor performance through Analytics
4. ✅ Identify areas where students need help
5. ✅ Allow students to retake tests for improvement

Enjoy using the OMR Sheet Submission System! 🎓
