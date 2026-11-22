/**
 * NoticePilot — Frontend Application Logic
 * Pure Vanilla JavaScript (ES6+), Zero External Libraries.
 */

'use strict';

// ============================================================================
// CONSTANTS & DEMO DATA
// ============================================================================

const STORAGE_KEYS = {
  HISTORY: 'noticepilot_history',
  TASKS: 'noticepilot_tasks',
  CURRENT: 'noticepilot_current_analysis'
};

const DEMO_NOTICES = {
  1: `Subject: Invitation to National Level Technical Workshop on AI & Machine Learning

Dear Students,

The Department of Computer Science and Engineering is organizing a National Level Technical Workshop on "Artificial Intelligence & Machine Learning: From Theory to Practice" in collaboration with Google Developer Student Clubs.

Date: 15th December 2026
Time: 9:00 AM to 5:00 PM
Venue: Seminar Hall, Block A, 3rd Floor

Key Highlights:
- Hands-on session with TensorFlow and PyTorch
- Industry expert speakers from Google and Microsoft
- Certificate of participation for all attendees
- Best project award worth Rs. 10,000

Registration Details:
- Registration deadline: 10th December 2026
- Registration fee: Rs. 500 (includes lunch and workshop materials)
- Register online at: https://college-events.example.com/ai-workshop

Requirements:
- Bring your own laptop with Python 3.8+ installed
- Basic knowledge of Python programming is mandatory
- Students must carry their college ID card

Contact Information:
Dr. Priya Sharma - priya.sharma@college.edu - 9876543210
Prof. Rahul Verma - rahul.verma@college.edu

Note: Limited seats available. First come, first served basis. Only 120 seats.

Regards,
Head of Department
Computer Science and Engineering`,

  2: `NOTICE

Date: 20th November 2026

All students of 3rd and 4th year B.Tech are hereby informed that a Guest Lecture on "Cybersecurity in the Age of AI" will be conducted as part of our Expert Lecture Series.

Speaker: Mr. Rajesh Kumar, Chief Security Officer, Infosys Ltd.

Date of Lecture: 28th November 2026
Time: 2:00 PM - 4:00 PM
Venue: Auditorium, Main Building

Attendance is mandatory for all CSE and IT students. Students must be seated by 1:45 PM. Latecomers will not be allowed entry after 2:15 PM.

Students are required to:
1. Carry a notebook and pen
2. Submit a one-page report within 3 days of the lecture
3. Dress code: Formal attire

For queries, contact the Training & Placement Cell:
Email: tnp@college.edu
Phone: 011-2345-6789

- Dr. Amit Patel
  Dean of Academics`,

  3: `EXAMINATION NOTICE

Ref No: EXAM/2026/Nov/047
Date: 18th November 2026

This is to notify all students that the End Semester Examinations for the Odd Semester 2026-27 will commence as per the following schedule:

Examination Period: 1st December 2026 to 15th December 2026
Reporting Time: 9:30 AM (30 minutes before exam)
Exam Duration: 3 hours (10:00 AM to 1:00 PM)

Important Deadlines:
- Last date to pay examination fee: 25th November 2026
- Hall ticket download available from: 28th November 2026
- Last date for exam form submission: 23rd November 2026

Instructions:
- Students must carry their hall ticket and college ID to the examination hall
- Use of electronic devices including smartwatches is strictly prohibited
- Students with outstanding fees will NOT be allowed to appear for examinations
- Medical students must submit fitness certificate if claiming medical leave

Exam Fee:
- Regular students: Rs. 1,500
- Backlog papers: Rs. 500 per subject

Contact the Examination Cell for any queries:
Room 102, Administrative Block
Email: examcell@college.edu
Phone: 011-9876-5432

Controller of Examinations`
};

// ============================================================================
// APPLICATION STATE
// ============================================================================

const state = {
  geminiAvailable: false,
  currentAnalysis: null,
  history: [],
  tasks: [],
  taskFilter: 'all', // 'all' | 'pending' | 'completed'
  taskSort: 'priority', // 'priority' | 'deadline' | 'name'
  isAnalyzing: false
};

// ============================================================================
// DOM ELEMENTS SELECTORS
// ============================================================================

const elements = {};

function initElementSelectors() {
  elements.aiStatusPill = document.getElementById('ai-status-pill');
  elements.aiStatusDot = document.getElementById('ai-status-dot');
  elements.aiStatusText = document.getElementById('ai-status-text');
  elements.aiToggleContainer = document.getElementById('ai-toggle-container');
  elements.useAiCheckbox = document.getElementById('use-ai-checkbox');

  // Stats
  elements.statTotalAnalyses = document.getElementById('stat-total-analyses');
  elements.statPendingTasks = document.getElementById('stat-pending-tasks');
  elements.statCompletedTasks = document.getElementById('stat-completed-tasks');
  elements.statUpcomingDeadlines = document.getElementById('stat-upcoming-deadlines');

  // Notice Input
  elements.noticeInput = document.getElementById('notice-text-input');
  elements.charCounter = document.getElementById('char-counter');
  elements.inputError = document.getElementById('input-error');
  elements.clearInputBtn = document.getElementById('clear-input-btn');
  elements.analyzeBtn = document.getElementById('analyze-btn');
  elements.analyzeBtnText = document.getElementById('analyze-btn-text');
  elements.analyzeSpinner = document.getElementById('analyze-spinner');
  elements.analyzeIcon = document.getElementById('analyze-icon');

  // Demo Buttons
  elements.demoBtn1 = document.getElementById('demo-btn-1');
  elements.demoBtn2 = document.getElementById('demo-btn-2');
  elements.demoBtn3 = document.getElementById('demo-btn-3');

  // Results Section
  elements.resultsSection = document.getElementById('results-section');
  elements.navLinkResults = document.getElementById('nav-link-results');
  elements.extractionMethodBadge = document.getElementById('extraction-method-badge');
  elements.extractionMethodText = document.getElementById('extraction-method-text');
  elements.analysisTimestamp = document.getElementById('analysis-timestamp');
  elements.analysisSummaryText = document.getElementById('analysis-summary-text');
  elements.exportCalendarBtn = document.getElementById('export-calendar-btn');
  elements.shareWhatsappBtn = document.getElementById('share-whatsapp-btn');
  elements.saveHistoryBtn = document.getElementById('save-history-btn');

  // Extracted Fields Grid
  elements.extractedFieldsGrid = document.getElementById('extracted-fields-grid');
  elements.fieldValTitle = document.getElementById('field-val-title');
  elements.fieldValDate = document.getElementById('field-val-date');
  elements.fieldValTime = document.getElementById('field-val-time');
  elements.fieldValLocation = document.getElementById('field-val-location');
  elements.fieldValRegDeadline = document.getElementById('field-val-registration_deadline');

  // Multi-item Lists
  elements.requirementsList = document.getElementById('requirements-list');
  elements.contactInfoList = document.getElementById('contact-info-list');
  elements.actionItemsList = document.getElementById('action-items-list');
  elements.addReqBtn = document.getElementById('add-req-btn');
  elements.addContactBtn = document.getElementById('add-contact-btn');
  elements.addActionItemBtn = document.getElementById('add-action-item-btn');

  // Task Board
  elements.tasksSection = document.getElementById('tasks-section');
  elements.tasksGrid = document.getElementById('tasks-grid');
  elements.tasksEmptyState = document.getElementById('tasks-empty-state');
  elements.tasksCounterBadge = document.getElementById('tasks-counter-badge');
  elements.taskSortSelect = document.getElementById('task-sort-select');
  elements.addCustomTaskBtn = document.getElementById('add-custom-task-btn');
  elements.filterButtons = document.querySelectorAll('.btn-filter');

  // History Section
  elements.historyList = document.getElementById('history-list');
  elements.historyEmptyState = document.getElementById('history-empty-state');
  elements.historyCounterBadge = document.getElementById('history-counter-badge');
  elements.clearHistoryBtn = document.getElementById('clear-history-btn');

  // Modals
  elements.whatsappModal = document.getElementById('whatsapp-modal');
  elements.whatsappPreview = document.getElementById('whatsapp-summary-preview');
  elements.copyWhatsappBtn = document.getElementById('copy-whatsapp-btn');
  elements.openWhatsappLink = document.getElementById('open-whatsapp-link');
  elements.closeWhatsappModal = document.getElementById('close-whatsapp-modal');
  elements.cancelWhatsappModal = document.getElementById('cancel-whatsapp-modal');

  elements.taskModal = document.getElementById('task-modal');
  elements.taskModalTitle = document.getElementById('task-modal-title');
  elements.taskForm = document.getElementById('task-form');
  elements.taskFormId = document.getElementById('task-form-id');
  elements.taskFormName = document.getElementById('task-form-name');
  elements.taskFormDeadline = document.getElementById('task-form-deadline');
  elements.taskFormPriority = document.getElementById('task-form-priority');
  elements.taskFormDesc = document.getElementById('task-form-desc');
  elements.closeTaskModal = document.getElementById('close-task-modal');
  elements.cancelTaskModal = document.getElementById('cancel-task-modal');

  elements.itemModal = document.getElementById('item-modal');
  elements.itemModalTitle = document.getElementById('item-modal-title');
  elements.itemForm = document.getElementById('item-form');
  elements.itemFormTarget = document.getElementById('item-form-target');
  elements.itemFormIndex = document.getElementById('item-form-index');
  elements.itemFormLabel = document.getElementById('item-form-label');
  elements.itemFormInput = document.getElementById('item-form-input');
  elements.closeItemModal = document.getElementById('close-item-modal');
  elements.cancelItemModal = document.getElementById('cancel-item-modal');

  elements.confirmModal = document.getElementById('confirm-modal');
  elements.confirmModalTitle = document.getElementById('confirm-modal-title');
  elements.confirmModalMessage = document.getElementById('confirm-modal-message');
  elements.proceedConfirmModal = document.getElementById('proceed-confirm-modal');
  elements.closeConfirmModal = document.getElementById('close-confirm-modal');
  elements.cancelConfirmModal = document.getElementById('cancel-confirm-modal');

  elements.toastContainer = document.getElementById('toast-container');
}

// ============================================================================
// UTILITY FUNCTIONS (SANITIZATION, IDS, DATES)
// ============================================================================

/**
 * Escapes HTML characters to prevent XSS attacks.
 * @param {string} str - Raw string
 * @returns {string} Sanitized string
 */
function escapeHTML(str) {
  if (typeof str !== 'string') return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Generates a unique pseudo-random ID.
 * @returns {string}
 */
function generateId() {
  return 'id_' + Math.random().toString(36).substring(2, 9) + Date.now().toString(36);
}

/**
 * Formats a date string or timestamp into a friendly human format.
 * @param {string|number|Date} dateInput
 * @returns {string}
 */
function formatDate(dateInput) {
  if (!dateInput) return 'Not specified';
  const parsed = new Date(dateInput);
  if (isNaN(parsed.getTime())) {
    return String(dateInput);
  }
  return parsed.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
}

/**
 * Returns relative time ago (e.g. "Just now", "5m ago", "Yesterday").
 * @param {number} timestamp
 * @returns {string}
 */
function timeAgo(timestamp) {
  if (!timestamp) return 'Recently';
  const diffSec = Math.floor((Date.now() - timestamp) / 1000);
  if (diffSec < 60) return 'Just now';
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

/**
 * Checks if a deadline date is in the future.
 * @param {string} deadlineStr
 * @returns {boolean}
 */
function isUpcoming(deadlineStr) {
  if (!deadlineStr) return false;
  const deadlineDate = parseFlexibleDate(deadlineStr);
  if (!deadlineDate) return false;
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return deadlineDate >= now;
}

/**
 * Checks if a deadline date has passed.
 * @param {string} deadlineStr
 * @returns {boolean}
 */
function isOverdue(deadlineStr) {
  if (!deadlineStr) return false;
  const deadlineDate = parseFlexibleDate(deadlineStr);
  if (!deadlineDate) return false;
  const now = new Date();
  now.setHours(0, 0, 0, 0);
  return deadlineDate < now;
}

/**
 * Helper to parse various human date formats (e.g., "15th December 2026", "2026-12-15").
 * @param {string} str
 * @returns {Date|null}
 */
function parseFlexibleDate(str) {
  if (!str) return null;
  // Clean ordinal suffixes like 1st, 2nd, 3rd, 15th
  const cleaned = str.replace(/(\d+)(st|nd|rd|th)/gi, '$1');
  const d = new Date(cleaned);
  return isNaN(d.getTime()) ? null : d;
}

// ============================================================================
// TOAST NOTIFICATION SYSTEM
// ============================================================================

/**
 * Displays a toast notification.
 * @param {string} message
 * @param {'success'|'error'|'info'|'warning'} [type='info']
 * @param {number} [duration=4000]
 */
function showToast(message, type = 'info', duration = 4000) {
  if (!elements.toastContainer) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.setAttribute('role', 'status');

  let iconSvg = '';
  switch (type) {
    case 'success':
      iconSvg = `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`;
      break;
    case 'error':
      iconSvg = `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
      break;
    case 'warning':
      iconSvg = `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>`;
      break;
    default:
      iconSvg = `<svg class="toast-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
  }

  toast.innerHTML = `
    ${iconSvg}
    <div class="toast-content">${escapeHTML(message)}</div>
    <button type="button" class="toast-close" aria-label="Dismiss toast">&times;</button>
  `;

  const closeBtn = toast.querySelector('.toast-close');
  const removeToast = () => {
    toast.classList.add('toast-fade-out');
    setTimeout(() => {
      if (toast.parentNode) {
        toast.parentNode.removeChild(toast);
      }
    }, 250);
  };

  closeBtn.addEventListener('click', removeToast);
  elements.toastContainer.appendChild(toast);

  if (duration > 0) {
    setTimeout(removeToast, duration);
  }
}

// ============================================================================
// STORAGE & STATE MANAGEMENT
// ============================================================================

function loadStorageData() {
  try {
    const rawHistory = localStorage.getItem(STORAGE_KEYS.HISTORY);
    state.history = rawHistory ? JSON.parse(rawHistory) : [];
  } catch (err) {
    console.warn('Failed to parse history from localStorage', err);
    state.history = [];
  }

  try {
    const rawTasks = localStorage.getItem(STORAGE_KEYS.TASKS);
    state.tasks = rawTasks ? JSON.parse(rawTasks) : [];
  } catch (err) {
    console.warn('Failed to parse tasks from localStorage', err);
    state.tasks = [];
  }

  try {
    const rawCurrent = localStorage.getItem(STORAGE_KEYS.CURRENT);
    state.currentAnalysis = rawCurrent ? JSON.parse(rawCurrent) : null;
  } catch (err) {
    console.warn('Failed to parse current analysis', err);
    state.currentAnalysis = null;
  }
}

function saveHistoryToStorage() {
  try {
    if (state.history.length > 50) {
      state.history = state.history.slice(0, 50);
    }
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(state.history));
  } catch (err) {
    console.error('Failed to save history to storage', err);
  }
}

function saveTasksToStorage() {
  try {
    localStorage.setItem(STORAGE_KEYS.TASKS, JSON.stringify(state.tasks));
  } catch (err) {
    console.error('Failed to save tasks to storage', err);
  }
}

function saveCurrentToStorage() {
  try {
    if (state.currentAnalysis) {
      localStorage.setItem(STORAGE_KEYS.CURRENT, JSON.stringify(state.currentAnalysis));
    } else {
      localStorage.removeItem(STORAGE_KEYS.CURRENT);
    }
  } catch (err) {
    console.error('Failed to save current analysis', err);
  }
}

// ============================================================================
// DASHBOARD STATS CALCULATION
// ============================================================================

function updateDashboardStats() {
  const totalAnalyses = state.history.length;
  const pendingTasks = state.tasks.filter(t => !t.completed).length;
  const completedTasks = state.tasks.filter(t => t.completed).length;

  // Upcoming deadlines: non-completed tasks with future deadline
  const upcomingDeadlines = state.tasks.filter(t => !t.completed && isUpcoming(t.deadline)).length;

  animateCounter(elements.statTotalAnalyses, totalAnalyses);
  animateCounter(elements.statPendingTasks, pendingTasks);
  animateCounter(elements.statCompletedTasks, completedTasks);
  animateCounter(elements.statUpcomingDeadlines, upcomingDeadlines);

  // Update tasks counter badge
  if (elements.tasksCounterBadge) {
    elements.tasksCounterBadge.textContent = `${state.tasks.length} task${state.tasks.length === 1 ? '' : 's'}`;
  }

  // Update history counter badge
  if (elements.historyCounterBadge) {
    elements.historyCounterBadge.textContent = `${state.history.length} saved`;
  }
}

function animateCounter(elem, targetValue) {
  if (!elem) return;
  const current = parseInt(elem.textContent, 10) || 0;
  if (current === targetValue) {
    elem.textContent = String(targetValue);
    return;
  }

  const diff = targetValue - current;
  const step = Math.ceil(Math.abs(diff) / 10) * (diff > 0 ? 1 : -1);

  let val = current;
  const interval = setInterval(() => {
    val += step;
    if ((diff > 0 && val >= targetValue) || (diff < 0 && val <= targetValue)) {
      elem.textContent = String(targetValue);
      clearInterval(interval);
    } else {
      elem.textContent = String(val);
    }
  }, 20);
}

// ============================================================================
// GEMINI STATUS CHECK
// ============================================================================

async function checkGeminiStatus() {
  if (!elements.aiStatusPill || !elements.aiStatusDot || !elements.aiStatusText) return;

  try {
    // Primary status endpoint
    const res = await fetch('/api/gemini-status');
    if (res.ok) {
      const data = await res.json();
      state.geminiAvailable = Boolean(data.available);
    } else {
      // Fallback check to /health endpoint
      const healthRes = await fetch('/health');
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        state.geminiAvailable = Boolean(healthData.gemini_available);
      } else {
        state.geminiAvailable = false;
      }
    }
  } catch (err) {
    // Network or server offline; default to local engine
    state.geminiAvailable = false;
  }

  updateGeminiStatusUI();
}

function updateGeminiStatusUI() {
  if (!elements.aiStatusDot || !elements.aiStatusText) return;

  elements.aiStatusDot.classList.remove('status-dot-checking', 'status-dot-online', 'status-dot-offline');

  if (state.geminiAvailable) {
    elements.aiStatusDot.classList.add('status-dot-online');
    elements.aiStatusText.textContent = 'Gemini AI Ready';
    elements.aiStatusPill.title = 'Google Gemini AI is connected and available for extraction';
    if (elements.aiToggleContainer) {
      elements.aiToggleContainer.style.display = 'flex';
      elements.useAiCheckbox.disabled = false;
    }
  } else {
    elements.aiStatusDot.classList.add('status-dot-offline');
    elements.aiStatusText.textContent = 'Local Engine (AI Offline)';
    elements.aiStatusPill.title = 'AI is unavailable. Local regex/rule extraction engine is active.';
    if (elements.aiToggleContainer) {
      elements.aiToggleContainer.style.display = 'none';
      elements.useAiCheckbox.checked = false;
      elements.useAiCheckbox.disabled = true;
    }
  }
}

// ============================================================================
// NOTICE INPUT & VALIDATION
// ============================================================================

function handleNoticeInput() {
  const text = elements.noticeInput.value;
  const count = text.length;
  const max = 10000;

  elements.charCounter.textContent = `${count.toLocaleString()} / ${max.toLocaleString()} characters`;

  elements.charCounter.classList.remove('warning', 'limit');
  if (count > max * 0.85 && count <= max) {
    elements.charCounter.classList.add('warning');
  } else if (count >= max) {
    elements.charCounter.classList.add('limit');
  }

  if (count > 0 && !elements.inputError.classList.contains('hidden')) {
    elements.inputError.classList.add('hidden');
    elements.inputError.textContent = '';
  }
}

function clearNoticeInput() {
  elements.noticeInput.value = '';
  handleNoticeInput();
  elements.inputError.classList.add('hidden');
  elements.inputError.textContent = '';
  elements.noticeInput.focus();
}

function loadDemoNotice(demoIndex) {
  const content = DEMO_NOTICES[demoIndex];
  if (!content) return;

  elements.noticeInput.value = content;
  handleNoticeInput();
  elements.noticeInput.focus();
  showToast(`Loaded Demo ${demoIndex} into notice input.`, 'info');
}

// ============================================================================
// NOTICE ANALYSIS (POST /api/analyze)
// ============================================================================

async function analyzeNotice() {
  const text = elements.noticeInput.value.trim();

  // Validation
  if (!text) {
    elements.inputError.textContent = 'Please paste a notice or select a demo notice above.';
    elements.inputError.classList.remove('hidden');
    elements.noticeInput.focus();
    showToast('Notice text cannot be empty.', 'warning');
    return;
  }

  if (text.length > 10000) {
    elements.inputError.textContent = 'Notice text exceeds the maximum limit of 10,000 characters.';
    elements.inputError.classList.remove('hidden');
    elements.noticeInput.focus();
    showToast('Notice exceeds 10,000 character limit.', 'error');
    return;
  }

  if (text.length < 20) {
    elements.inputError.textContent = 'Notice text is too brief for structured extraction (minimum 20 characters).';
    elements.inputError.classList.remove('hidden');
    elements.noticeInput.focus();
    showToast('Notice is too brief to analyze.', 'warning');
    return;
  }

  setAnalyzingState(true);

  const useAi = state.geminiAvailable && elements.useAiCheckbox.checked;

  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text: text,
        use_ai: useAi
      })
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || `Server returned status ${response.status}`);
    }

    const data = await response.json();
    handleAnalysisSuccess(data, text);
    showToast('Notice analyzed successfully!', 'success');
  } catch (err) {
    console.error('Analysis error:', err);
    showToast(`Analysis failed: ${err.message}`, 'error');
  } finally {
    setAnalyzingState(false);
  }
}

function setAnalyzingState(isAnalyzing) {
  state.isAnalyzing = isAnalyzing;
  elements.analyzeBtn.disabled = isAnalyzing;

  if (isAnalyzing) {
    elements.analyzeSpinner.classList.remove('hidden');
    elements.analyzeIcon.classList.add('hidden');
    elements.analyzeBtnText.textContent = 'Extracting Details...';
  } else {
    elements.analyzeSpinner.classList.add('hidden');
    elements.analyzeIcon.classList.remove('hidden');
    elements.analyzeBtnText.textContent = 'Analyze Notice';
  }
}

function handleAnalysisSuccess(data, originalText) {
  const analysisRecord = {
    id: generateId(),
    timestamp: Date.now(),
    original_text: originalText,
    extracted_info: data.extracted_info || {},
    tasks: data.tasks || [],
    summary: data.summary || '',
    extraction_method: data.extraction_method || 'Local Engine'
  };

  state.currentAnalysis = analysisRecord;
  saveCurrentToStorage();

  // Merge generated tasks into global task board
  if (Array.isArray(analysisRecord.tasks) && analysisRecord.tasks.length > 0) {
    analysisRecord.tasks.forEach(task => {
      // Ensure each task has valid required fields
      const taskObj = {
        id: task.id || generateId(),
        name: task.name || 'Untitled Action Item',
        deadline: task.deadline || null,
        priority: task.priority || 'Medium',
        completed: Boolean(task.completed),
        description: task.description || '',
        sourceNoticeId: analysisRecord.id,
        createdAt: Date.now()
      };
      state.tasks.unshift(taskObj);
    });
    saveTasksToStorage();
  }

  // Prepend to history
  state.history.unshift({
    id: analysisRecord.id,
    timestamp: analysisRecord.timestamp,
    title: analysisRecord.extracted_info.title || 'Untitled Notice',
    tasks_count: (analysisRecord.tasks || []).length,
    extraction_method: analysisRecord.extraction_method,
    extracted_info: analysisRecord.extracted_info,
    tasks: analysisRecord.tasks,
    summary: analysisRecord.summary,
    original_text: originalText
  });
  saveHistoryToStorage();

  // Render UI
  renderResultsSection();
  renderTasks();
  renderHistory();
  updateDashboardStats();

  // Smooth scroll to results
  if (elements.resultsSection) {
    elements.resultsSection.classList.remove('hidden');
    if (elements.navLinkResults) {
      elements.navLinkResults.classList.remove('hidden');
    }
    setTimeout(() => {
      elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }
}

// ============================================================================
// EXTRACTION RESULTS RENDERING
// ============================================================================

function renderResultsSection() {
  if (!state.currentAnalysis) {
    if (elements.resultsSection) elements.resultsSection.classList.add('hidden');
    if (elements.navLinkResults) elements.navLinkResults.classList.add('hidden');
    return;
  }

  const { extracted_info, extraction_method, timestamp, summary } = state.currentAnalysis;

  // Header info
  elements.resultsSection.classList.remove('hidden');
  if (elements.navLinkResults) elements.navLinkResults.classList.remove('hidden');

  if (elements.extractionMethodText) {
    elements.extractionMethodText.textContent = extraction_method || 'Local Engine';
  }

  if (elements.analysisTimestamp) {
    elements.analysisTimestamp.textContent = timeAgo(timestamp);
  }

  if (elements.analysisSummaryText) {
    elements.analysisSummaryText.textContent = summary || 'Verified structured notice breakdown with traceable evidence.';
  }

  // Evidence lookup map: fieldName -> { snippet, confidence }
  const evidenceMap = {};
  if (Array.isArray(extracted_info.evidence)) {
    extracted_info.evidence.forEach(item => {
      if (item.field) {
        evidenceMap[item.field.toLowerCase()] = item;
      }
    });
  }

  const uncertainSet = new Set((extracted_info.uncertain_fields || []).map(f => f.toLowerCase()));

  // Render 5 Primary Structured Fields
  renderFieldCard('title', extracted_info.title, evidenceMap['title'], uncertainSet.has('title'));
  renderFieldCard('date', extracted_info.date, evidenceMap['date'], uncertainSet.has('date'));
  renderFieldCard('time', extracted_info.time, evidenceMap['time'], uncertainSet.has('time'));
  renderFieldCard('location', extracted_info.location, evidenceMap['location'], uncertainSet.has('location'));
  renderFieldCard('registration_deadline', extracted_info.registration_deadline, evidenceMap['registration_deadline'], uncertainSet.has('registration_deadline'));

  // Render Lists
  renderDetailList(elements.requirementsList, extracted_info.requirements, 'requirements');
  renderDetailList(elements.contactInfoList, extracted_info.contact_info, 'contact_info');
  renderDetailList(elements.actionItemsList, extracted_info.action_items, 'action_items');
}

function renderFieldCard(fieldKey, value, evidence, isUncertain) {
  const cardElem = document.getElementById(`field-card-${fieldKey}`);
  const valElem = document.getElementById(`field-val-${fieldKey}`);
  const indicatorsElem = document.getElementById(`indicators-${fieldKey}`);
  const evidenceElem = document.getElementById(`evidence-${fieldKey}`);

  if (!cardElem || !valElem) return;

  // Set Value
  valElem.textContent = value || 'Not specified';
  if (!value) {
    valElem.style.color = 'var(--text-muted)';
    valElem.style.fontWeight = '400';
  } else {
    valElem.style.color = 'var(--text-primary)';
    valElem.style.fontWeight = '600';
  }

  // Uncertain flag style
  if (isUncertain) {
    cardElem.classList.add('is-uncertain');
  } else {
    cardElem.classList.remove('is-uncertain');
  }

  // Build Indicators (Confidence dot + Uncertain warning icon)
  if (indicatorsElem) {
    indicatorsElem.innerHTML = '';

    if (isUncertain) {
      const warnSpan = document.createElement('span');
      warnSpan.className = 'uncertain-flag';
      warnSpan.title = 'Field marked as uncertain by extraction engine';
      warnSpan.innerHTML = '⚠️';
      indicatorsElem.appendChild(warnSpan);
    }

    if (evidence && typeof evidence.confidence === 'number') {
      const conf = evidence.confidence;
      let confClass = 'conf-high';
      let confLabel = `${Math.round(conf * 100)}%`;

      if (conf < 0.5) {
        confClass = 'conf-low';
      } else if (conf <= 0.8) {
        confClass = 'conf-medium';
      }

      const confBadge = document.createElement('span');
      confBadge.className = `confidence-indicator ${confClass}`;
      confBadge.title = `Confidence: ${(conf * 100).toFixed(1)}%`;
      confBadge.innerHTML = `<span class="conf-dot"></span>${confLabel}`;
      indicatorsElem.appendChild(confBadge);
    }
  }

  // Evidence Quote Snippet
  if (evidenceElem) {
    if (evidence && evidence.snippet) {
      evidenceElem.textContent = `“${evidence.snippet}”`;
      evidenceElem.style.display = 'block';
    } else {
      evidenceElem.textContent = '';
      evidenceElem.style.display = 'none';
    }
  }
}

function renderDetailList(containerElem, itemsArray, targetKey) {
  if (!containerElem) return;

  containerElem.innerHTML = '';

  if (!Array.isArray(itemsArray) || itemsArray.length === 0) {
    const emptyLi = document.createElement('li');
    emptyLi.className = 'empty-list-notice';
    emptyLi.textContent = `No ${targetKey.replace('_', ' ')} detected.`;
    containerElem.appendChild(emptyLi);
    return;
  }

  itemsArray.forEach((itemText, index) => {
    const li = document.createElement('li');
    li.className = 'detail-item';

    li.innerHTML = `
      <span class="detail-item-content">${escapeHTML(itemText)}</span>
      <div class="detail-item-actions">
        <button type="button" class="btn-item-action edit-item-btn" data-target="${targetKey}" data-index="${index}" title="Edit item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
        </button>
        <button type="button" class="btn-item-action delete-item-btn" data-target="${targetKey}" data-index="${index}" title="Remove item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
        </button>
      </div>
    `;

    containerElem.appendChild(li);
  });
}

// ============================================================================
// TASK BOARD MANAGEMENT
// ============================================================================

function renderTasks() {
  if (!elements.tasksGrid) return;

  let filtered = [...state.tasks];

  // Filter
  if (state.taskFilter === 'pending') {
    filtered = filtered.filter(t => !t.completed);
  } else if (state.taskFilter === 'completed') {
    filtered = filtered.filter(t => t.completed);
  }

  // Sort
  if (state.taskSort === 'priority') {
    const priorityWeight = { 'High': 3, 'Medium': 2, 'Low': 1 };
    filtered.sort((a, b) => {
      const wa = priorityWeight[a.priority] || 1;
      const wb = priorityWeight[b.priority] || 1;
      return wb - wa;
    });
  } else if (state.taskSort === 'deadline') {
    filtered.sort((a, b) => {
      if (!a.deadline) return 1;
      if (!b.deadline) return -1;
      const da = parseFlexibleDate(a.deadline) || new Date(9999, 11, 31);
      const db = parseFlexibleDate(b.deadline) || new Date(9999, 11, 31);
      return da - db;
    });
  } else if (state.taskSort === 'name') {
    filtered.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
  }

  elements.tasksGrid.innerHTML = '';

  if (filtered.length === 0) {
    if (elements.tasksEmptyState) {
      elements.tasksGrid.appendChild(elements.tasksEmptyState);
      elements.tasksEmptyState.style.display = 'flex';
    }
    return;
  }

  filtered.forEach(task => {
    const card = createTaskCardElement(task);
    elements.tasksGrid.appendChild(card);
  });
}

function createTaskCardElement(task) {
  const card = document.createElement('div');
  card.className = `task-card ${task.completed ? 'is-completed' : ''}`;
  card.dataset.taskId = task.id;

  const priorityLower = (task.priority || 'medium').toLowerCase();
  const priorityBadgeClass = `badge-priority-${priorityLower}`;

  let deadlineTagHtml = '';
  if (task.deadline) {
    const overdue = !task.completed && isOverdue(task.deadline);
    deadlineTagHtml = `
      <span class="task-deadline-tag ${overdue ? 'is-overdue' : ''}" title="${overdue ? 'Deadline passed' : 'Target deadline'}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
        ${escapeHTML(task.deadline)} ${overdue ? '(Overdue)' : ''}
      </span>
    `;
  } else {
    deadlineTagHtml = `
      <span class="task-deadline-tag" style="opacity: 0.5;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        No deadline
      </span>
    `;
  }

  card.innerHTML = `
    <div class="task-card-header">
      <div class="task-checkbox-wrap">
        <input 
          type="checkbox" 
          class="task-checkbox" 
          aria-label="Mark task ${escapeHTML(task.name)} complete" 
          ${task.completed ? 'checked' : ''}
          data-task-id="${escapeHTML(task.id)}"
        >
      </div>
      <div class="task-title-group">
        <div class="task-title">${escapeHTML(task.name)}</div>
        ${task.description ? `<p class="task-desc">${escapeHTML(task.description)}</p>` : ''}
      </div>
    </div>

    <div class="task-card-meta">
      <div style="display: flex; align-items: center; gap: 0.65rem;">
        <span class="badge ${priorityBadgeClass}">${escapeHTML(task.priority || 'Medium')}</span>
        ${deadlineTagHtml}
      </div>

      <div class="task-card-actions">
        <button type="button" class="btn-task-action edit-task-btn" data-task-id="${escapeHTML(task.id)}" title="Edit task details">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
        </button>
        <button type="button" class="btn-task-action delete delete-task-btn" data-task-id="${escapeHTML(task.id)}" title="Delete task">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
        </button>
      </div>
    </div>
  `;

  // Attach Checkbox event listener
  const checkbox = card.querySelector('.task-checkbox');
  checkbox.addEventListener('change', () => {
    toggleTaskCompletion(task.id, checkbox.checked);
  });

  return card;
}

function toggleTaskCompletion(taskId, completed) {
  const task = state.tasks.find(t => t.id === taskId);
  if (!task) return;

  task.completed = completed;
  saveTasksToStorage();
  renderTasks();
  updateDashboardStats();

  showToast(`Task "${task.name}" marked as ${completed ? 'completed' : 'pending'}.`, 'info', 2000);
}

function openTaskModal(task = null) {
  if (task) {
    elements.taskModalTitle.textContent = 'Edit Task';
    elements.taskFormId.value = task.id;
    elements.taskFormName.value = task.name || '';
    elements.taskFormDeadline.value = task.deadline || '';
    elements.taskFormPriority.value = task.priority || 'Medium';
    elements.taskFormDesc.value = task.description || '';
  } else {
    elements.taskModalTitle.textContent = 'Create New Task';
    elements.taskFormId.value = '';
    elements.taskFormName.value = '';
    elements.taskFormDeadline.value = '';
    elements.taskFormPriority.value = 'Medium';
    elements.taskFormDesc.value = '';
  }

  elements.taskModal.classList.remove('hidden');
  elements.taskFormName.focus();
}

function closeTaskModal() {
  elements.taskModal.classList.add('hidden');
}

function saveTaskFromModal(e) {
  e.preventDefault();

  const id = elements.taskFormId.value;
  const name = elements.taskFormName.value.trim();
  const deadline = elements.taskFormDeadline.value.trim() || null;
  const priority = elements.taskFormPriority.value;
  const desc = elements.taskFormDesc.value.trim();

  if (!name) {
    showToast('Task name is required', 'warning');
    return;
  }

  if (id) {
    // Updating existing task
    const task = state.tasks.find(t => t.id === id);
    if (task) {
      task.name = name;
      task.deadline = deadline;
      task.priority = priority;
      task.description = desc;
      showToast('Task updated successfully', 'success');
    }
  } else {
    // Creating new task
    const newTask = {
      id: generateId(),
      name: name,
      deadline: deadline,
      priority: priority,
      completed: false,
      description: desc,
      createdAt: Date.now()
    };
    state.tasks.unshift(newTask);
    showToast('New task added', 'success');
  }

  saveTasksToStorage();
  renderTasks();
  updateDashboardStats();
  closeTaskModal();
}

function promptDeleteTask(taskId) {
  const task = state.tasks.find(t => t.id === taskId);
  if (!task) return;

  openConfirmModal(
    'Delete Task',
    `Are you sure you want to delete "${task.name}"? This cannot be undone.`,
    () => {
      state.tasks = state.tasks.filter(t => t.id !== taskId);
      saveTasksToStorage();
      renderTasks();
      updateDashboardStats();
      showToast('Task deleted', 'info');
    }
  );
}

// ============================================================================
// HISTORY ARCHIVE MANAGEMENT
// ============================================================================

function renderHistory() {
  if (!elements.historyList) return;

  elements.historyList.innerHTML = '';

  if (state.history.length === 0) {
    if (elements.historyEmptyState) {
      elements.historyList.appendChild(elements.historyEmptyState);
      elements.historyEmptyState.style.display = 'flex';
    }
    return;
  }

  state.history.forEach(item => {
    const card = document.createElement('div');
    card.className = 'history-item-card';
    card.dataset.historyId = item.id;

    card.innerHTML = `
      <div class="history-item-info">
        <div class="history-item-title-row">
          <span class="history-item-title" title="Click to view details">${escapeHTML(item.title || 'Untitled Notice')}</span>
          <span class="badge badge-muted">${escapeHTML(item.extraction_method || 'Local')}</span>
        </div>
        <div class="history-item-meta">
          <span class="history-meta-entry">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            ${timeAgo(item.timestamp)}
          </span>
          <span class="history-meta-entry">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>
            ${item.tasks_count || 0} tasks
          </span>
        </div>
      </div>

      <div class="history-item-actions">
        <button type="button" class="btn btn-secondary btn-sm restore-history-btn" data-history-id="${escapeHTML(item.id)}">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>
          Restore
        </button>
        <button type="button" class="btn btn-danger-outline btn-sm delete-history-btn" data-history-id="${escapeHTML(item.id)}" title="Delete from history">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
        </button>
      </div>
    `;

    // Click title or restore button to restore
    const restoreTrigger = card.querySelector('.restore-history-btn');
    const titleTrigger = card.querySelector('.history-item-title');
    const deleteTrigger = card.querySelector('.delete-history-btn');

    const handleRestore = () => restoreHistoryItem(item.id);

    restoreTrigger.addEventListener('click', handleRestore);
    titleTrigger.addEventListener('click', handleRestore);

    deleteTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteHistoryItem(item.id);
    });

    elements.historyList.appendChild(card);
  });
}

function restoreHistoryItem(historyId) {
  const item = state.history.find(h => h.id === historyId);
  if (!item) return;

  state.currentAnalysis = {
    id: item.id,
    timestamp: item.timestamp,
    original_text: item.original_text || '',
    extracted_info: item.extracted_info || {},
    tasks: item.tasks || [],
    summary: item.summary || '',
    extraction_method: item.extraction_method || 'Local Engine'
  };

  saveCurrentToStorage();

  // Populate textarea
  if (item.original_text) {
    elements.noticeInput.value = item.original_text;
    handleNoticeInput();
  }

  renderResultsSection();
  updateDashboardStats();

  elements.resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  showToast(`Restored analysis: "${item.title}"`, 'success');
}

function deleteHistoryItem(historyId) {
  state.history = state.history.filter(h => h.id !== historyId);
  saveHistoryToStorage();
  renderHistory();
  updateDashboardStats();
  showToast('Removed from history', 'info');
}

function clearAllHistory() {
  if (state.history.length === 0) return;

  openConfirmModal(
    'Clear All History',
    'Are you sure you want to permanently clear all saved notice analyses? This cannot be undone.',
    () => {
      state.history = [];
      saveHistoryToStorage();
      renderHistory();
      updateDashboardStats();
      showToast('All history cleared', 'info');
    }
  );
}

// ============================================================================
// CALENDAR (.ICS) EXPORT (POST /api/export/ics)
// ============================================================================

async function exportToCalendar() {
  if (!state.currentAnalysis || !state.currentAnalysis.extracted_info) {
    showToast('No notice analysis available to export', 'warning');
    return;
  }

  const info = state.currentAnalysis.extracted_info;

  if (!info.date) {
    showToast('Cannot export to calendar: Event date is missing. Please edit and set a date first.', 'warning');
    return;
  }

  const payload = {
    title: info.title || 'College Event',
    date: info.date,
    time: info.time || null,
    location: info.location || null,
    description: state.currentAnalysis.summary || (info.requirements ? info.requirements.join('\n') : ''),
    all_day: !info.time
  };

  try {
    showToast('Generating calendar file...', 'info', 2000);
    const response = await fetch('/api/export/ics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const blob = await response.blob();
      downloadBlob(blob, `${slugify(payload.title || 'notice_event')}.ics`);
      showToast('Calendar (.ics) file downloaded!', 'success');
    } else {
      const err = await response.json().catch(() => ({}));
      showToast(err.detail || 'Failed to export calendar event: Invalid or missing date.', 'error');
    }
  } catch (err) {
    console.warn('Backend ICS generation failed, attempting client-side export', err);
    generateClientSideIcs(payload);
  }
}

function generateClientSideIcs(payload) {
  if (!payload.date) {
    showToast('Cannot export calendar event: Event date is missing.', 'error');
    return;
  }

  const d = parseFlexibleDate(payload.date);
  if (!d) {
    showToast('Cannot export calendar event: Invalid date format.', 'error');
    return;
  }

  const title = payload.title || 'College Event';
  const location = payload.location || '';
  const description = payload.description || '';

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const dateFormatted = `${year}${month}${day}`;

  const icsContent = [
    'BEGIN:VCALENDAR',
    'VERSION:2.0',
    'PRODID:-//NoticePilot//College Notice Events//EN',
    'CALSCALE:GREGORIAN',
    'BEGIN:VEVENT',
    `SUMMARY:${title}`,
    `LOCATION:${location}`,
    `DESCRIPTION:${description.replace(/\n/g, '\\n')}`,
    `DTSTART;VALUE=DATE:${dateFormatted}`,
    `DTEND;VALUE=DATE:${dateFormatted}`,
    `UID:${generateId()}@noticepilot.app`,
    'STATUS:CONFIRMED',
    'END:VEVENT',
    'END:VCALENDAR'
  ].join('\r\n');

  const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
  downloadBlob(blob, `${slugify(title)}.ics`);
  showToast('Calendar (.ics) downloaded successfully!', 'success');
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function slugify(text) {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '_')
    .replace(/[^\w-]+/g, '')
    .substring(0, 40);
}

// ============================================================================
// WHATSAPP SHARING (POST /api/share/whatsapp)
// ============================================================================

async function shareViaWhatsApp() {
  if (!state.currentAnalysis) {
    showToast('No active notice analysis to share', 'warning');
    return;
  }

  const { extracted_info, tasks } = state.currentAnalysis;

  try {
    const res = await fetch('/api/share/whatsapp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        extracted_info: extracted_info || {},
        tasks: tasks || []
      })
    });

    if (res.ok) {
      const data = await res.json();
      openWhatsAppModal(data.summary);
    } else {
      // Fallback client-side formatter
      openWhatsAppModal(formatClientSideWhatsApp(extracted_info, tasks));
    }
  } catch (err) {
    console.warn('Backend whatsapp formatter failed, using local format', err);
    openWhatsAppModal(formatClientSideWhatsApp(extracted_info, tasks));
  }
}

function formatClientSideWhatsApp(info, tasks) {
  const lines = [];
  lines.push(`📢 *${(info.title || 'College Notice').toUpperCase()}*`);
  lines.push('────────────────────────');

  if (info.date) lines.push(`📅 *Date:* ${info.date}`);
  if (info.time) lines.push(`⏰ *Time:* ${info.time}`);
  if (info.location) lines.push(`📍 *Venue:* ${info.location}`);
  if (info.registration_deadline) lines.push(`⏳ *Registration Deadline:* ${info.registration_deadline}`);

  if (Array.isArray(info.requirements) && info.requirements.length > 0) {
    lines.push('\n📝 *Requirements:*');
    info.requirements.forEach(r => lines.push(`• ${r}`));
  }

  if (Array.isArray(tasks) && tasks.length > 0) {
    lines.push('\n✅ *Action Items:*');
    tasks.forEach(t => lines.push(`• [${t.priority}] ${t.name}${t.deadline ? ` (by ${t.deadline})` : ''}`));
  }

  if (Array.isArray(info.contact_info) && info.contact_info.length > 0) {
    lines.push('\n📞 *Contact Info:*');
    info.contact_info.forEach(c => lines.push(`• ${c}`));
  }

  lines.push('\n_Generated via NoticePilot ✈️_');
  return lines.join('\n');
}

function openWhatsAppModal(summaryText) {
  elements.whatsappPreview.textContent = summaryText;

  // Direct WhatsApp web link
  const encoded = encodeURIComponent(summaryText);
  elements.openWhatsappLink.href = `https://api.whatsapp.com/send?text=${encoded}`;

  elements.whatsappModal.classList.remove('hidden');
}

function closeWhatsAppModal() {
  elements.whatsappModal.classList.add('hidden');
}

async function copyWhatsAppText() {
  const text = elements.whatsappPreview.textContent;
  if (!text) return;

  let copied = false;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    try {
      await navigator.clipboard.writeText(text);
      copied = true;
    } catch (e) {
      copied = false;
    }
  }

  if (!copied) {
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.opacity = '0';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      copied = document.execCommand('copy');
      document.body.removeChild(textArea);
    } catch (err) {
      copied = false;
    }
  }

  showToast('Summary copied to clipboard!', 'success');
}

// ============================================================================
// INLINE / MODAL FIELD EDITING
// ============================================================================

function openEditFieldModal(fieldKey) {
  if (!state.currentAnalysis || !state.currentAnalysis.extracted_info) return;

  const currentVal = state.currentAnalysis.extracted_info[fieldKey] || '';
  const labelMap = {
    title: 'Notice / Event Title',
    date: 'Event Date',
    time: 'Time',
    location: 'Location / Venue',
    registration_deadline: 'Registration Deadline'
  };

  elements.itemModalTitle.textContent = `Edit ${labelMap[fieldKey] || fieldKey}`;
  elements.itemFormLabel.textContent = labelMap[fieldKey] || fieldKey;
  elements.itemFormTarget.value = `field:${fieldKey}`;
  elements.itemFormIndex.value = '';
  elements.itemFormInput.value = currentVal;

  elements.itemModal.classList.remove('hidden');
  elements.itemFormInput.focus();
}

function openAddDetailModal(targetKey) {
  const labelMap = {
    requirements: 'New Requirement',
    contact_info: 'New Contact Info',
    action_items: 'New Action Item'
  };

  elements.itemModalTitle.textContent = `Add ${labelMap[targetKey] || 'Item'}`;
  elements.itemFormLabel.textContent = labelMap[targetKey] || 'Value';
  elements.itemFormTarget.value = `list:${targetKey}`;
  elements.itemFormIndex.value = '-1';
  elements.itemFormInput.value = '';

  elements.itemModal.classList.remove('hidden');
  elements.itemFormInput.focus();
}

function openEditDetailModal(targetKey, index) {
  if (!state.currentAnalysis || !state.currentAnalysis.extracted_info) return;

  const list = state.currentAnalysis.extracted_info[targetKey] || [];
  const currentVal = list[index] || '';

  elements.itemModalTitle.textContent = `Edit Item`;
  elements.itemFormLabel.textContent = 'Description';
  elements.itemFormTarget.value = `list:${targetKey}`;
  elements.itemFormIndex.value = String(index);
  elements.itemFormInput.value = currentVal;

  elements.itemModal.classList.remove('hidden');
  elements.itemFormInput.focus();
}

function closeItemModal() {
  elements.itemModal.classList.add('hidden');
}

function handleSaveItemModal(e) {
  e.preventDefault();
  if (!state.currentAnalysis || !state.currentAnalysis.extracted_info) return;

  const target = elements.itemFormTarget.value;
  const indexStr = elements.itemFormIndex.value;
  const val = elements.itemFormInput.value.trim();

  if (target.startsWith('field:')) {
    const fieldKey = target.replace('field:', '');
    state.currentAnalysis.extracted_info[fieldKey] = val || null;
    saveCurrentToStorage();
    renderResultsSection();
    showToast(`Updated ${fieldKey}`, 'success');
  } else if (target.startsWith('list:')) {
    const listKey = target.replace('list:', '');
    if (!Array.isArray(state.currentAnalysis.extracted_info[listKey])) {
      state.currentAnalysis.extracted_info[listKey] = [];
    }
    const list = state.currentAnalysis.extracted_info[listKey];
    const index = parseInt(indexStr, 10);

    if (index >= 0 && index < list.length) {
      if (val) {
        list[index] = val;
      } else {
        list.splice(index, 1);
      }
    } else if (val) {
      list.push(val);
    }
    saveCurrentToStorage();
    renderResultsSection();
    showToast('Updated list item', 'success');
  }

  closeItemModal();
}

function deleteDetailListItem(targetKey, index) {
  if (!state.currentAnalysis || !state.currentAnalysis.extracted_info) return;
  const list = state.currentAnalysis.extracted_info[targetKey];
  if (!Array.isArray(list) || index < 0 || index >= list.length) return;

  list.splice(index, 1);
  saveCurrentToStorage();
  renderResultsSection();
  showToast('Item removed', 'info');
}

// ============================================================================
// CONFIRM DIALOG
// ============================================================================

let confirmCallback = null;

function openConfirmModal(title, message, onProceed) {
  elements.confirmModalTitle.textContent = title;
  elements.confirmModalMessage.textContent = message;
  confirmCallback = onProceed;
  elements.confirmModal.classList.remove('hidden');
}

function closeConfirmModal() {
  elements.confirmModal.classList.add('hidden');
  confirmCallback = null;
}

// ============================================================================
// EVENT LISTENERS INITIALIZATION
// ============================================================================

function setupEventListeners() {
  // Input handling
  elements.noticeInput.addEventListener('input', handleNoticeInput);
  elements.clearInputBtn.addEventListener('click', clearNoticeInput);
  elements.analyzeBtn.addEventListener('click', analyzeNotice);

  // Demo Buttons
  elements.demoBtn1.addEventListener('click', () => loadDemoNotice(1));
  elements.demoBtn2.addEventListener('click', () => loadDemoNotice(2));
  elements.demoBtn3.addEventListener('click', () => loadDemoNotice(3));

  // Results Section Actions
  elements.exportCalendarBtn.addEventListener('click', exportToCalendar);
  elements.shareWhatsappBtn.addEventListener('click', shareViaWhatsApp);
  elements.saveHistoryBtn.addEventListener('click', () => {
    if (state.currentAnalysis) {
      showToast('Analysis is saved in LocalStorage.', 'success');
    }
  });

  // Edit Field Buttons on Structured Cards
  document.querySelectorAll('.btn-edit-field').forEach(btn => {
    btn.addEventListener('click', () => {
      const fieldKey = btn.dataset.target;
      openEditFieldModal(fieldKey);
    });
  });

  // Add Item Buttons on Detail Lists
  elements.addReqBtn.addEventListener('click', () => openAddDetailModal('requirements'));
  elements.addContactBtn.addEventListener('click', () => openAddDetailModal('contact_info'));
  elements.addActionItemBtn.addEventListener('click', () => openAddDetailModal('action_items'));

  // Edit/Delete delegated events for detail lists
  [elements.requirementsList, elements.contactInfoList, elements.actionItemsList].forEach(container => {
    container.addEventListener('click', (e) => {
      const editBtn = e.target.closest('.edit-item-btn');
      if (editBtn) {
        const target = editBtn.dataset.target;
        const index = parseInt(editBtn.dataset.index, 10);
        openEditDetailModal(target, index);
        return;
      }

      const deleteBtn = e.target.closest('.delete-item-btn');
      if (deleteBtn) {
        const target = deleteBtn.dataset.target;
        const index = parseInt(deleteBtn.dataset.index, 10);
        deleteDetailListItem(target, index);
      }
    });
  });

  // Task Board Controls
  elements.filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      elements.filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.taskFilter = btn.dataset.filter;
      renderTasks();
    });
  });

  elements.taskSortSelect.addEventListener('change', (e) => {
    state.taskSort = e.target.value;
    renderTasks();
  });

  elements.addCustomTaskBtn.addEventListener('click', () => openTaskModal(null));

  // Task Grid Event Delegation (Edit & Delete)
  elements.tasksGrid.addEventListener('click', (e) => {
    const editBtn = e.target.closest('.edit-task-btn');
    if (editBtn) {
      const taskId = editBtn.dataset.taskId;
      const task = state.tasks.find(t => t.id === taskId);
      if (task) openTaskModal(task);
      return;
    }

    const deleteBtn = e.target.closest('.delete-task-btn');
    if (deleteBtn) {
      const taskId = deleteBtn.dataset.taskId;
      promptDeleteTask(taskId);
    }
  });

  // History Controls
  elements.clearHistoryBtn.addEventListener('click', clearAllHistory);

  // Modals Close & Form Actions
  elements.closeWhatsappModal.addEventListener('click', closeWhatsAppModal);
  elements.cancelWhatsappModal.addEventListener('click', closeWhatsAppModal);
  elements.copyWhatsappBtn.addEventListener('click', copyWhatsAppText);

  elements.closeTaskModal.addEventListener('click', closeTaskModal);
  elements.cancelTaskModal.addEventListener('click', closeTaskModal);
  elements.taskForm.addEventListener('submit', saveTaskFromModal);

  elements.closeItemModal.addEventListener('click', closeItemModal);
  elements.cancelItemModal.addEventListener('click', closeItemModal);
  elements.itemForm.addEventListener('submit', handleSaveItemModal);

  elements.closeConfirmModal.addEventListener('click', closeConfirmModal);
  elements.cancelConfirmModal.addEventListener('click', closeConfirmModal);
  elements.proceedConfirmModal.addEventListener('click', () => {
    if (typeof confirmCallback === 'function') {
      confirmCallback();
    }
    closeConfirmModal();
  });

  // Close modals when clicking backdrop
  [elements.whatsappModal, elements.taskModal, elements.itemModal, elements.confirmModal].forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.add('hidden');
      }
    });
  });

  // Keyboard accessibility: ESC key closes open modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      [elements.whatsappModal, elements.taskModal, elements.itemModal, elements.confirmModal].forEach(m => {
        if (!m.classList.contains('hidden')) {
          m.classList.add('hidden');
        }
      });
    }
  });
}

// ============================================================================
// APP BOOTSTRAP (DOMContentLoaded)
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
  initElementSelectors();
  loadStorageData();
  setupEventListeners();

  // Initial UI renders
  updateDashboardStats();
  renderTasks();
  renderHistory();

  // If there's an existing active analysis, render it
  if (state.currentAnalysis) {
    renderResultsSection();
    if (state.currentAnalysis.original_text) {
      elements.noticeInput.value = state.currentAnalysis.original_text;
      handleNoticeInput();
    }
  }

  // Check Gemini AI availability
  checkGeminiStatus();
});
