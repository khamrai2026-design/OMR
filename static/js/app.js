// Global state
let appState = {
    chapters: [],
    currentChapter: null,
    currentAnswers: {},
    selectedAttempt: null,
    lastExamAttempt: null,
    historyActiveAttempt: null,
    timerRunning: false,
    timerPaused: false,
    timerSeconds: 0,
    timerInterval: null,
    examStartTime: null,
    examEndTime: null
};

// Initialize app on load
document.addEventListener('DOMContentLoaded', () => {
    loadChapters();
    loadResultsChapters();
    setupNavigation();
    initializeTheme();
});

// ==================== Theme Management ====================
const themeConfigs = {
    indigo: { primary: '#6366f1', primaryDark: '#4f46e5', secondary: '#ec4899', accent: '#8b5cf6' },
    ocean: { primary: '#0891b2', primaryDark: '#0e7490', secondary: '#06b6d4', accent: '#00d9ff' },
    forest: { primary: '#059669', primaryDark: '#047857', secondary: '#10b981', accent: '#34d399' },
    sunset: { primary: '#ea580c', primaryDark: '#c2410c', secondary: '#f97316', accent: '#fb923c' },
    violet: { primary: '#9333ea', primaryDark: '#7e22ce', secondary: '#a855f7', accent: '#d946ef' },
    slate: { primary: '#64748b', primaryDark: '#475569', secondary: '#475569', accent: '#78716c' },
    rose: { primary: '#e11d48', primaryDark: '#be185d', secondary: '#f43f5e', accent: '#fb7185' },
    emerald: { primary: '#10b981', primaryDark: '#059669', secondary: '#34d399', accent: '#6ee7b7' },
    amber: { primary: '#f59e0b', primaryDark: '#d97706', secondary: '#fbbf24', accent: '#fcd34d' },
    coral: { primary: '#ff6b6b', primaryDark: '#ff5252', secondary: '#ff8787', accent: '#ffa5a5' },
    cyberpunk: { primary: '#ec0aff', primaryDark: '#d000e8', secondary: '#00ffff', accent: '#00ff88' },
    teal: { primary: '#14b8a6', primaryDark: '#0d9488', secondary: '#2dd4bf', accent: '#5eead4' },
    sky: { primary: '#0ea5e9', primaryDark: '#0284c7', secondary: '#38bdf8', accent: '#7dd3fc' }
};

function initializeTheme() {
    const savedTheme = localStorage.getItem('selectedTheme') || 'indigo';
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.value = savedTheme;
    }
    applyTheme(savedTheme);
}

function changeTheme(themeName) {
    localStorage.setItem('selectedTheme', themeName);
    applyTheme(themeName);
}

function applyTheme(themeName) {
    const theme = themeConfigs[themeName];
    if (!theme) return;
    
    const root = document.documentElement;
    root.style.setProperty('--primary', theme.primary);
    root.style.setProperty('--primary-dark', theme.primaryDark);
    root.style.setProperty('--secondary', theme.secondary);
    root.style.setProperty('--accent', theme.accent);
    
    // Update theme select dropdown
    const themeSelect = document.getElementById('themeSelect');
    if (themeSelect) {
        themeSelect.value = themeName;
    }
}

// ==================== Timer Management ====================
function startTimer() {
    if (appState.timerRunning) return;
    
    appState.timerRunning = true;
    appState.timerPaused = false;
    updateTimerButton();
    
    appState.timerInterval = setInterval(() => {
        if (!appState.timerPaused) {
            appState.timerSeconds++;
            updateTimerDisplay();
        }
    }, 1000);
}

function toggleTimer() {
    if (!appState.timerRunning) {
        startTimer();
        return;
    }
    
    appState.timerPaused = !appState.timerPaused;
    updateTimerButton();
}

function stopTimer() {
    if (appState.timerInterval) {
        clearInterval(appState.timerInterval);
        appState.timerInterval = null;
    }
    appState.timerRunning = false;
    appState.timerPaused = false;
}

function updateTimerDisplay() {
    const hours = Math.floor(appState.timerSeconds / 3600);
    const minutes = Math.floor((appState.timerSeconds % 3600) / 60);
    const seconds = appState.timerSeconds % 60;
    
    const timeString = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timerValue').textContent = timeString;
}

function updateTimerButton() {
    const btn = document.getElementById('timerBtn');
    if (!btn) return;
    
    if (appState.timerPaused) {
        btn.textContent = '▶️ Resume';
        btn.classList.remove('playing');
        document.querySelector('.timer-display').classList.add('paused');
    } else {
        btn.textContent = '⏸️ Pause';
        btn.classList.add('playing');
        document.querySelector('.timer-display').classList.remove('paused');
    }
}

function getTimeTaken() {
    return appState.timerSeconds;
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

// ==================== Custom Alerts ====================
function showAlert(message, type = 'warning') {
    const overlay = document.getElementById('alertOverlay');
    if (!overlay) return;

    const icons = {
        warning: '⚠️',
        error: '❌',
        success: '✅',
        info: 'ℹ️'
    };

    const alert = document.createElement('div');
    alert.className = `custom-alert alert-${type}`;
    alert.innerHTML = `
        <span class="alert-icon">${icons[type] || 'ℹ️'}</span>
        <div class="alert-content">${message}</div>
    `;

    overlay.innerHTML = ''; // Keep only one alert at a time
    overlay.appendChild(alert);

    // Trigger animation
    setTimeout(() => overlay.classList.add('show'), 10);

    // Auto dismiss
    setTimeout(() => {
        overlay.classList.remove('show');
        setTimeout(() => alert.remove(), 400);
    }, 3000);
}

// ==================== Navigation ==================== 
function showPage(pageId) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });

    // Show selected page
    document.getElementById(pageId).classList.add('active');

    // Update nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    event.target.classList.add('active');

    // Load page-specific data
    if (pageId === 'results') {
        loadResultsChapters();
    } else if (pageId === 'analytics') {
        loadAnalytics();
    }
}

function setupNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            const pageId = link.textContent.toLowerCase().match(/exam|results|analytics/)[0];
            const page = pageId === 'results' ? 'results' : pageId;
            showPage(page);

            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
            link.classList.add('active');
        });
    });
}

// ==================== Chapters ==================== 
async function loadChapters() {
    try {
        const response = await fetch('/api/chapters');
        const chapters = await response.json();
        appState.chapters = chapters;

        // Populate exam select
        const select = document.getElementById('chapterSelect');
        select.innerHTML = chapters.length > 0
            ? chapters.map(ch => `<option value="${ch.id}">${ch.chapter_name}</option>`).join('')
            : '<option value="">No chapters found</option>';
    } catch (error) {
        console.error('Error loading chapters:', error);
    }
}

function updateTakeExamButton() {
    const chapterId = document.getElementById('chapterSelect').value;
    const takeExamBtn = document.getElementById('takeExamBtn');
    
    if (chapterId) {
        takeExamBtn.style.display = 'block';
    } else {
        takeExamBtn.style.display = 'none';
    }
}

function initiateExam() {
    const studentName = document.getElementById('studentName').value;
    
    if (!studentName) {
        showAlert('Please enter your name before taking exam', 'warning');
        return;
    }
    
    loadChapterDetails();
}

async function loadChapterDetails() {
    const chapterId = document.getElementById('chapterSelect').value;
    const chapterName = document.getElementById('chapterSelect').options[document.getElementById('chapterSelect').selectedIndex].text;
    const studentName = document.getElementById('studentName').value;

    if (!chapterId) return;

    try {
        const response = await fetch(`/api/chapter/${chapterId}`);
        const chapter = await response.json();
        appState.currentChapter = chapter;

        // Fetch attempt count for this student and chapter
        let attemptNumber = 1;
        try {
            const resultsResponse = await fetch(`/api/results/${chapterName}`);
            const attempts = await resultsResponse.json();
            const studentAttempts = attempts.filter(a => a.student_name === studentName);
            attemptNumber = studentAttempts.length + 1;
        } catch (e) {
            console.log('Could not fetch attempt count, defaulting to 1');
        }

        // Show attempt info with attempt number
        const attemptInfo = document.getElementById('attemptInfo');
        attemptInfo.textContent = `📍 Attempting #${attemptNumber} for this chapter`;
        attemptInfo.style.display = 'block';

        // Show answer sheet
        document.getElementById('answerSheet').style.display = 'block';
        document.getElementById('resultCard').style.display = 'none';

        // Check if resuming an existing attempt
        const timerKey = getTimerKey();
        const existingTimer = localStorage.getItem(timerKey);
        
        if (!existingTimer) {
            // Fresh exam - reset timer and record start time
            stopTimer();
            appState.timerSeconds = 0;
            appState.examStartTime = new Date();
            updateTimerDisplay();
        } else if (!appState.examStartTime) {
            // Resuming exam - estimate start time from elapsed seconds
            const now = new Date();
            appState.examStartTime = new Date(now.getTime() - (appState.timerSeconds * 1000));
        }
        
        // Render questions
        renderQuestions(chapter);
        
        // Load saved answers (which also restores timer if it exists)
        loadSavedAnswers();
        
        // Only start/resume timer if not already running
        if (!appState.timerRunning) {
            startTimer();
        } else if (appState.timerPaused) {
            // If it was paused, keep it paused
            appState.timerPaused = true;
            updateTimerButton();
        }

    } catch (error) {
        console.error('Error loading chapter details:', error);
    }
}

function renderQuestions(chapter) {
    const optionLetters = [];
    for (let i = 0; i < chapter.num_options; i++) {
        optionLetters.push(String.fromCharCode(65 + i));
    }

    // Update question info
    document.getElementById('questionInfo').textContent =
        `${chapter.num_questions} questions • Options: ${optionLetters.join(', ')}`;

    const container = document.getElementById('questionsContainer');
    container.innerHTML = '';
    appState.currentAnswers = {};

    for (let i = 0; i < chapter.num_questions; i++) {
        const questionGroup = document.createElement('div');
        questionGroup.className = 'question-group';
        questionGroup.style.setProperty('--question-num', `"${i + 1}"`);

        const label = document.createElement('div');
        label.className = 'question-label';
        label.textContent = `Question ${i + 1}`;
        label.setAttribute('data-question', i + 1);

        const optionsGrid = document.createElement('div');
        optionsGrid.className = 'options-grid';

        optionLetters.forEach(option => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'option-btn';
            btn.textContent = option;
            btn.onclick = (e) => {
                e.preventDefault();
                // Remove selected from siblings
                btn.parentElement.querySelectorAll('.option-btn').forEach(b => {
                    b.classList.remove('selected');
                });
                // Add selected to current
                btn.classList.add('selected');
                appState.currentAnswers[i] = option;
                
                // Auto-save answers
                saveAttemptedAnswers();
            };
            optionsGrid.appendChild(btn);
        });

        questionGroup.appendChild(label);
        questionGroup.appendChild(optionsGrid);
        container.appendChild(questionGroup);
    }
    
    // Load previously saved answers for this chapter
    loadSavedAnswers();
}

// ==================== Answer Saving & Recovery ====================
function getAttemptKey() {
    const studentName = document.getElementById('studentName').value;
    const chapterId = document.getElementById('chapterSelect').value;
    return `exam_attempt_${studentName}_${chapterId}`;
}

function getTimerKey() {
    const studentName = document.getElementById('studentName').value;
    const chapterId = document.getElementById('chapterSelect').value;
    return `exam_timer_${studentName}_${chapterId}`;
}

function saveAttemptedAnswers() {
    const key = getAttemptKey();
    const savedData = {
        answers: appState.currentAnswers,
        timestamp: new Date().toISOString(),
        studentName: document.getElementById('studentName').value,
        chapterId: document.getElementById('chapterSelect').value,
        elapsedSeconds: appState.timerSeconds
    };
    localStorage.setItem(key, JSON.stringify(savedData));
    
    // Save timer state separately
    const timerKey = getTimerKey();
    const timerData = {
        elapsedSeconds: appState.timerSeconds,
        isPaused: appState.timerPaused,
        lastSavedAt: new Date().toISOString()
    };
    localStorage.setItem(timerKey, JSON.stringify(timerData));
    
    // Show save indicator (optional)
    showSaveIndicator();
}

function loadSavedAnswers() {
    const key = getAttemptKey();
    const savedData = localStorage.getItem(key);
    const timerKey = getTimerKey();
    const timerData = localStorage.getItem(timerKey);
    
    // Restore timer state first
    if (timerData) {
        try {
            const timer = JSON.parse(timerData);
            appState.timerSeconds = timer.elapsedSeconds;
            appState.timerPaused = timer.isPaused;
            updateTimerDisplay();
            updateTimerButton();
            console.log(`Restored timer: ${timer.elapsedSeconds} seconds, paused: ${timer.isPaused}`);
        } catch (e) {
            console.log('Could not restore timer state');
        }
    }
    
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            appState.currentAnswers = data.answers;
            
            // Restore selected buttons
            const container = document.getElementById('questionsContainer');
            Object.entries(appState.currentAnswers).forEach(([questionIndex, answer]) => {
                const questionIndex_num = parseInt(questionIndex);
                const buttons = container.querySelectorAll('.question-group')[questionIndex_num]?.querySelectorAll('.option-btn');
                if (buttons) {
                    buttons.forEach(btn => {
                        if (btn.textContent === answer) {
                            btn.classList.add('selected');
                        }
                    });
                }
            });
            
            console.log('Restored saved answers');
        } catch (e) {
            console.log('Could not load saved answers');
        }
    }
}

function clearSavedAnswers() {
    const key = getAttemptKey();
    const timerKey = getTimerKey();
    localStorage.removeItem(key);
    localStorage.removeItem(timerKey);
}

function showSaveIndicator() {
    const indicator = document.getElementById('saveIndicator');
    if (!indicator) {
        const newIndicator = document.createElement('div');
        newIndicator.id = 'saveIndicator';
        newIndicator.style.position = 'fixed';
        newIndicator.style.bottom = '20px';
        newIndicator.style.right = '20px';
        newIndicator.style.background = '#10b981';
        newIndicator.style.color = 'white';
        newIndicator.style.padding = '10px 16px';
        newIndicator.style.borderRadius = '8px';
        newIndicator.style.fontSize = '0.9rem';
        newIndicator.style.fontWeight = '600';
        newIndicator.style.zIndex = '999';
        newIndicator.style.opacity = '0.9';
        newIndicator.style.transition = 'opacity 0.3s ease';
        newIndicator.textContent = '💾 Answers Saved';
        document.body.appendChild(newIndicator);
        
        // Remove after 2 seconds
        setTimeout(() => {
            newIndicator.style.opacity = '0';
            setTimeout(() => newIndicator.remove(), 300);
        }, 2000);
    }
}

// ==================== Exam Submission ==================== 
async function submitExam() {
    const studentName = document.getElementById('studentName').value;
    const chapterId = document.getElementById('chapterSelect').value;

    if (!studentName) {
        showAlert('Please enter your name', 'warning');
        return;
    }

    if (!chapterId) {
        showAlert('Please select a chapter', 'warning');
        return;
    }

    // Check all questions answered
    const numQuestions = appState.currentChapter.num_questions;
    const answeredCount = Object.keys(appState.currentAnswers).length;

    if (answeredCount < numQuestions) {
        const remaining = numQuestions - answeredCount;
        showAlert(`Please answer all questions! You have ${remaining} remaining.`, 'warning');

        // Highlight unanswered
        highlightUnanswered();
        return;
    }

    // Convert answers object to array
    const submittedAnswers = [];
    for (let i = 0; i < numQuestions; i++) {
        submittedAnswers.push(appState.currentAnswers[i] || null);
    }
    
    // Stop timer and record end time
    stopTimer();
    appState.examEndTime = new Date();
    const timeTaken = appState.timerSeconds;

    try {
        const response = await fetch('/api/submit-exam', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_name: studentName,
                chapter_id: parseInt(chapterId),
                submitted_answers: submittedAnswers,
                time_taken: timeTaken,
                start_time: appState.examStartTime.toISOString(),
                end_time: appState.examEndTime.toISOString()
            })
        });

        const result = await response.json();

        if (result.success) {
            // Clear saved answers
            clearSavedAnswers();
            
            // Show results
            displayResults(result, submittedAnswers, timeTaken);

            // Show confetti effect
            confetti();
            showAlert('Excellent! Your examination has been submitted.', 'success');
        } else {
            showAlert('Error: ' + result.message, 'error');
        }
    } catch (error) {
        console.error('Error submitting exam:', error);
        showAlert('Error submitting exam. Please check your connection.', 'error');
    }
}

function highlightUnanswered() {
    const questions = document.querySelectorAll('.question-group');
    questions.forEach((group, index) => {
        const isAnswered = appState.currentAnswers[index] !== undefined;
        if (!isAnswered) {
            group.style.borderColor = 'var(--error)';
            group.classList.add('shake-animation');
            setTimeout(() => {
                group.style.borderColor = '';
                group.classList.remove('shake-animation');
            }, 3000);
        }
    });
}

function displayResults(result, submittedAnswers, timeTaken = 0) {
    // Hide answer sheet, show results
    document.getElementById('answerSheet').style.display = 'none';
    document.getElementById('resultCard').style.display = 'block';

    // Update metrics
    document.getElementById('immediateScoreDisplay').textContent = `${result.score}/${result.total}`;
    document.getElementById('immediatePercentageDisplay').textContent = `${result.percentage.toFixed(1)}%`;
    document.getElementById('attemptDisplay').textContent = result.attempt_number;
    document.getElementById('immediateTimeDisplay').textContent = formatTime(timeTaken);

    // Build answer table
    const tbody = document.getElementById('answerTableBody');
    tbody.innerHTML = '';

    submittedAnswers.forEach((answer, index) => {
        const correct = result.correct_answers[index];
        const isCorrect = answer === correct;

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${answer || 'Not Answered'}</td>
            <td>${correct}</td>
            <td><span class="status-badge ${isCorrect ? 'status-correct' : 'status-incorrect'}">
                ${isCorrect ? '✅ Correct' : '❌ Wrong'}
            </span></td>
        `;
        tbody.appendChild(tr);
    });

    // Also render the luxury grid view
    const attemptData = {
        submitted_answers: submittedAnswers,
        correct_answers: result.correct_answers,
        total_questions: result.total,
        time_taken: timeTaken
    };
    appState.lastExamAttempt = attemptData;
    renderQuestionReview(attemptData, 'immediateQuestionReview');

    // Scroll to results
    document.getElementById('resultCard').scrollIntoView({ behavior: 'smooth' });
}

// ==================== Export Functions ====================
async function exportExamResult() {
    const studentName = document.getElementById('studentName').value;
    const chapterId = document.getElementById('chapterSelect').value;
    const score = document.getElementById('immediateScoreDisplay').textContent.split('/')[0];
    const totalQuestions = document.getElementById('immediateScoreDisplay').textContent.split('/')[1];
    const percentage = parseFloat(document.getElementById('immediatePercentageDisplay').textContent);
    const attemptNumber = parseInt(document.getElementById('attemptDisplay').textContent);
    
    if (!appState.lastExamAttempt) {
        showAlert('No exam result to export', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/export/exam', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_name: studentName,
                chapter_name: appState.currentChapter.chapter_name,
                score: parseInt(score),
                total_questions: parseInt(totalQuestions),
                percentage: percentage,
                attempt_number: attemptNumber,
                submitted_answers: appState.lastExamAttempt.submitted_answers,
                correct_answers: appState.lastExamAttempt.correct_answers,
                submitted_at: new Date().toLocaleString()
            })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        // Get the blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `OMR_Report_${studentName}_${appState.currentChapter.chapter_name}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showAlert('✅ Exam report exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting exam:', error);
        showAlert('Failed to export exam report. Please try again.', 'error');
    }
}

async function exportChapterResults(chapterName) {
    if (!chapterName) {
        showAlert('Please select a chapter', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/export/chapter-results', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chapter_name: chapterName
            })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        // Get the blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `Chapter_Results_${chapterName}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showAlert('✅ Chapter results exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting chapter results:', error);
        showAlert('Failed to export chapter results. Please try again.', 'error');
    }
}

async function exportHistoryResult() {
    if (!appState.historyActiveAttempt) {
        showAlert('Please select an attempt to export', 'warning');
        return;
    }
    
    const attempt = appState.historyActiveAttempt;
    
    try {
        const response = await fetch('/api/export/exam', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                student_name: attempt.student_name,
                chapter_name: attempt.chapter_name,
                score: attempt.score,
                total_questions: attempt.total_questions,
                percentage: (attempt.score / attempt.total_questions * 100),
                attempt_number: attempt.attempt_number,
                submitted_answers: JSON.parse(attempt.submitted_answers || '[]'),
                correct_answers: JSON.parse(attempt.correct_answers || '[]'),
                submitted_at: attempt.submitted_at
            })
        });
        
        if (!response.ok) {
            throw new Error('Export failed');
        }
        
        // Get the blob and download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `OMR_Report_${attempt.student_name}_${attempt.chapter_name}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        showAlert('✅ Result exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting result:', error);
        showAlert('Failed to export result. Please try again.', 'error');
    }
}

// Simple confetti effect
function confetti() {
    const colors = ['#6366f1', '#0891b2', '#10b981', '#f59e0b', '#ef4444'];
    for (let i = 0; i < 50; i++) {
        const conf = document.createElement('div');
        conf.style.position = 'fixed';
        conf.style.width = '10px';
        conf.style.height = '10px';
        conf.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        conf.style.borderRadius = '50%';
        conf.style.left = Math.random() * window.innerWidth + 'px';
        conf.style.top = '-10px';
        conf.style.opacity = '1';
        conf.style.transition = 'all 3s ease-out';
        conf.style.zIndex = '999';

        document.body.appendChild(conf);

        setTimeout(() => {
            conf.style.top = window.innerHeight + 'px';
            conf.style.opacity = '0';
        }, 10);

        setTimeout(() => conf.remove(), 3000);
    }
}

// ==================== Results ==================== 
async function loadResultsChapters() {
    try {
        const response = await fetch('/api/chapters');
        const chapters = await response.json();

        const select = document.getElementById('resultsChapterSelect');
        select.innerHTML = '<option value="">Select a chapter...</option>';

        chapters.forEach(chapter => {
            const option = document.createElement('option');
            option.value = chapter.chapter_name;
            option.textContent = chapter.chapter_name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading chapters:', error);
    }
}

async function loadResults() {
    const chapterName = document.getElementById('resultsChapterSelect').value;

    if (!chapterName) return;

    try {
        const response = await fetch(`/api/results/${chapterName}`);
        const attempts = await response.json();

        const attemptSelect = document.getElementById('attemptSelect');
        const historySection = document.getElementById('attemptHistory');

        if (attempts.length === 0) {
            attemptSelect.innerHTML = '<option value="">No attempts found</option>';
            historySection.style.display = 'none';
            return;
        }

        attemptSelect.innerHTML = '';
        attempts.forEach((attempt, idx) => {
            const option = document.createElement('option');
            const date = new Date(attempt.submitted_at).toLocaleDateString();
            option.value = idx;
            option.textContent = `Attempt ${attempt.attempt_number} - ${attempt.score}/${attempt.total_questions} - ${date}`;
            attemptSelect.appendChild(option);
        });

        // Display history
        const tbody = document.getElementById('attemptHistoryBody');
        tbody.innerHTML = '';
        attempts.forEach(attempt => {
            const score = attempt.score || 0;
            const total = attempt.total_questions || 1;
            const percentage = ((score / total) * 100).toFixed(1);
            const grade = getGrade(percentage);
            const date = new Date(attempt.submitted_at).toLocaleDateString();
            const time = formatTime(attempt.time_taken || 0);

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#${attempt.attempt_number}</td>
                <td>${score}/${total}</td>
                <td>${percentage}%</td>
                <td>${grade}</td>
                <td>${time}</td>
                <td>${date}</td>
                <td><button onclick="showAttemptDetails()" class="btn btn-sm">View</button></td>
            `;
            tbody.appendChild(tr);
        });

        historySection.style.display = 'block';

        // Show first attempt by default
        if (attempts.length > 0) {
            attemptSelect.value = '0';
            showAttemptDetails();
        }
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

function showAttemptDetails() {
    const chapterName = document.getElementById('resultsChapterSelect').value;
    const attemptIdx = parseInt(document.getElementById('attemptSelect').value);

    if (!chapterName || attemptIdx === undefined) return;

    fetch(`/api/results/${chapterName}`)
        .then(r => r.json())
        .then(attempts => {
            const attempt = attempts[attemptIdx];
            if (!attempt) return;

            const score = attempt.score || 0;
            const total = attempt.total_questions || 1;
            const percentage = ((score / total) * 100).toFixed(1);
            const grade = getGrade(percentage);
            const isPassed = percentage >= 60;

            // Update metrics
            document.getElementById('totalScoreDisplay').textContent = `${score}/${total}`;
            document.getElementById('correctDisplay').textContent = score;
            document.getElementById('incorrectDisplay').textContent = total - score;
            document.getElementById('historyPercentageDisplay').textContent = percentage + '%';
            document.getElementById('timeDisplay').textContent = formatTime(attempt.time_taken || 0);
            document.getElementById('gradeDisplay').textContent = grade;

            // Update badge
            const badge = document.getElementById('resultBadge');
            badge.textContent = isPassed ? '✓ PASSED' : '✗ FAILED';
            badge.className = 'result-badge ' + (isPassed ? '' : 'fail');

            // Render question review
            appState.historyActiveAttempt = attempt;
            renderQuestionReview(attempt);

            document.getElementById('detailedResult').style.display = 'block';
        })
        .catch(error => console.error('Error showing attempt details:', error));
}

function setReviewFilter(filter, containerId) {
    // Update UI toggle
    const container = document.getElementById(containerId).parentElement;
    container.querySelectorAll('.filter-chip').forEach(chip => {
        chip.classList.toggle('active', chip.getAttribute('data-filter') === filter);
    });

    // Get data source
    const attempt = containerId === 'immediateQuestionReview'
        ? appState.lastExamAttempt
        : appState.historyActiveAttempt;

    if (attempt) {
        renderQuestionReview(attempt, containerId, filter);
    }
}

function renderQuestionReview(attempt, containerId = 'questionReview', filter = 'all') {
    const reviewDiv = document.getElementById(containerId);
    if (!reviewDiv) return;
    reviewDiv.innerHTML = '';

    // Parse answers and correct answers
    const answersData = attempt.answers || attempt.submitted_answers || '[]';
    const answers = typeof answersData === 'string' ? JSON.parse(answersData) : answersData;

    const correctData = attempt.correct_answers || '[]';
    const correctAnswers = typeof correctData === 'string' ? JSON.parse(correctData) : correctData;

    const numQuestions = attempt.total_questions || correctAnswers.length;

    let renderedCount = 0;

    // The question-review-grid class handles the layout
    for (let i = 0; i < numQuestions; i++) {
        const userAnswer = answers[i] || null;
        const correctAnswer = correctAnswers[i];
        const isCorrect = userAnswer === correctAnswer;
        const isUnanswered = userAnswer === null || userAnswer === '';

        // Filter logic: 'incorrect' shows anything NOT correct
        if (filter === 'incorrect' && isCorrect && !isUnanswered) continue;
        if (filter === 'correct' && !isCorrect) continue;

        renderedCount++;
        const card = document.createElement('div');
        // Dynamic class based on status
        card.className = 'question-review-card ' + (isUnanswered ? 'unanswered' : isCorrect ? 'correct' : 'incorrect');

        const statusIcon = isUnanswered ? '⚪ Unanswered' : isCorrect ? '✅ Correct' : '❌ Incorrect';

        card.innerHTML = `
            <div class="review-question-num">Question ${i + 1}</div>
            <div style="color: var(--text-muted); font-size: 0.9rem; margin: 0.5rem 0; font-weight: 600;">
                ${statusIcon}
            </div>
            <div class="review-answer-row">
                <div class="review-answer-item">
                    <div class="review-answer-label">Your Answer</div>
                    <div class="review-answer-value">${userAnswer || 'Not Answered'}</div>
                </div>
                <div class="review-answer-item">
                    <div class="review-answer-label">Correct Answer</div>
                    <div class="review-answer-value">${correctAnswer}</div>
                </div>
            </div>
        `;

        reviewDiv.appendChild(card);
    }

    if (renderedCount === 0) {
        reviewDiv.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3.5rem; color: var(--text-muted); background: rgba(0,0,0,0.02); border-radius: 16px; border: 2px dashed var(--border);">
                <div style="font-size: 3rem; margin-bottom: 1rem;">🎯</div>
                <p style="font-weight: 600; font-size: 1.1rem;">No questions match this filter.</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">Try selecting a different filter option above.</p>
            </div>
        `;
    }
}

function getGrade(percentage) {
    const pct = parseFloat(percentage);
    if (pct >= 90) return 'A';
    if (pct >= 80) return 'B';
    if (pct >= 70) return 'C';
    if (pct >= 60) return 'D';
    return 'F';
}

function formatTime(seconds) {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}h ${mins}m`;
    } else if (mins > 0) {
        return `${mins}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function exportResults() {
    const chapterName = document.getElementById('resultsChapterSelect').value;
    const attemptIdx = parseInt(document.getElementById('attemptSelect').value);

    if (!chapterName || attemptIdx === undefined) {
        alert('Please select an attempt to export');
        return;
    }

    // TODO: Implement Excel export
    alert('Export functionality coming soon!');
}

// ==================== Analytics ==================== 
let performanceChart = null;
let timeVsScoreChart = null;

async function loadAnalytics() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();

        // Load chapter filter
        const filterSelect = document.getElementById('analyticsChapterFilter');
        filterSelect.innerHTML = '<option value="">All Chapters</option>';
        if (data.chapter_stats) {
            data.chapter_stats.forEach(stat => {
                const option = document.createElement('option');
                option.value = stat.chapter_name || 'Unknown';
                option.textContent = stat.chapter_name || 'Unknown';
                filterSelect.appendChild(option);
            });
        }

        // Update KPIs
        document.getElementById('totalAttempts').textContent = data.total_attempts || 0;
        document.getElementById('avgScore').textContent = (data.avg_score || 0).toFixed(1);
        document.getElementById('bestScore').textContent = data.best_score || 0;
        document.getElementById('avgAccuracy').textContent = (data.avg_accuracy || 0).toFixed(1) + '%';

        // Chart rendering will happen in loadAnalyticsWithFilter
        loadAnalyticsWithFilter();
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

async function loadAnalyticsWithFilter() {
    try {
        const response = await fetch('/api/analytics');
        const data = await response.json();

        const chapterFilter = document.getElementById('analyticsChapterFilter').value;
        const dateFilter = document.getElementById('analyticsDateFilter').value;

        // Filter attempts if needed
        let filteredAttempts = data.all_attempts || [];
        if (chapterFilter) {
            filteredAttempts = filteredAttempts.filter(a => a.chapter_name === chapterFilter);
        }

        // Update chapter stats
        const tbody = document.getElementById('chapterStatsBody');
        tbody.innerHTML = '';
        if (data.chapter_stats) {
            data.chapter_stats.forEach(stat => {
                const tr = document.createElement('tr');
                const progress = ((stat.avg_percentage || 0) / 100 * 100).toFixed(0);
                tr.innerHTML = `
                    <td>${stat.chapter_name}</td>
                    <td>${stat.total_attempts || 0}</td>
                    <td>${stat.best_score || 0}</td>
                    <td>${(stat.avg_percentage || 0).toFixed(1)}</td>
                    <td>${(stat.avg_accuracy || 0).toFixed(1)}%</td>
                    <td>
                        <div class="progress-bar">
                            <div class="progress-bar-fill" style="width: ${progress}%"></div>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Update detailed stats
        const detailedBody = document.getElementById('detailedStatsBody');
        detailedBody.innerHTML = '';
        (filteredAttempts || []).forEach(attempt => {
            const percentage = ((attempt.score / attempt.total_questions) * 100).toFixed(1);
            const grade = getGrade(percentage);
            const date = new Date(attempt.submitted_at).toLocaleDateString();
            const time = formatTime(attempt.time_taken || 0);
            const isPassed = percentage >= 60;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${date}</td>
                <td>${attempt.chapter_name}</td>
                <td>${attempt.score}/${attempt.total_questions}</td>
                <td>${grade}</td>
                <td>${percentage}%</td>
                <td>${time}</td>
                <td>${isPassed ? '✓ Pass' : '✗ Fail'}</td>
            `;
            detailedBody.appendChild(tr);
        });

        // Render charts (if Chart.js available)
        if (typeof Chart !== 'undefined') {
            renderPerformanceTrendChart(filteredAttempts || []);
            renderTimeVsScoreChart(filteredAttempts || []);
        }
    } catch (error) {
        console.error('Error loading analytics:', error);
    }
}

function renderPerformanceTrendChart(attempts) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    // Sort by date
    const sorted = attempts.sort((a, b) => new Date(a.submitted_at) - new Date(b.submitted_at));

    const labels = sorted.map(a => new Date(a.submitted_at).toLocaleDateString());
    const scores = sorted.map(a => ((a.score / a.total_questions) * 100).toFixed(1));

    if (performanceChart) {
        performanceChart.destroy();
    }

    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score %',
                data: scores,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: '#6366f1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function renderTimeVsScoreChart(attempts) {
    const ctx = document.getElementById('timeVsScoreChart');
    if (!ctx) return;

    const times = attempts.map(a => a.time_taken || 0);
    const scores = attempts.map(a => ((a.score / a.total_questions) * 100).toFixed(1));

    if (timeVsScoreChart) {
        timeVsScoreChart.destroy();
    }

    timeVsScoreChart = new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Time vs Score',
                data: times.map((t, i) => ({ x: t / 60, y: scores[i] })),
                backgroundColor: 'rgba(8, 145, 178, 0.6)',
                borderColor: '#0891b2',
                borderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { display: true }
            },
            scales: {
                x: {
                    title: { display: true, text: 'Time (minutes)' }
                },
                y: {
                    title: { display: true, text: 'Score (%)' },
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function downloadAnalyticsReport() {
    alert('Download functionality coming soon!');
}

// Prevent form submission
document.addEventListener('submit', (e) => {
    if (e.target.id === 'examForm') {
        e.preventDefault();
    }
});
