// ========================================
// DASHBOARD.JS - AI Voice Diary
// ========================================

'use strict';

// ========================================
// SIDEBAR & NAVIGATION
// ========================================


/**
 * Initialize sidebar toggle functionality
 */
function initSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (sidebarToggle && sidebar && sidebarOverlay) {
        // Toggle sidebar on button click
        sidebarToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.classList.toggle('active');
            sidebarOverlay.classList.toggle('active');
        });

        // Close sidebar when clicking overlay
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        });

        // Close sidebar on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
                sidebarOverlay.classList.remove('active');
            }
        });
    }
}

/**
 * Highlight active navigation link based on current URL
 */
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ========================================
// MODE TOGGLE (Voice/Text)
// ========================================

/**
 * Initialize mode toggle buttons
 */
function initModeToggle() {
    const voiceModeBtn = document.getElementById('voiceModeBtn');
    const textModeBtn = document.getElementById('textModeBtn');
    const voiceInputArea = document.getElementById('voiceInputArea');
    const textInputArea = document.getElementById('textInputArea');
    
    if (voiceModeBtn && textModeBtn && voiceInputArea && textInputArea) {

        voiceModeBtn.addEventListener('click', () => {
            voiceModeBtn.classList.add('active');
            textModeBtn.classList.remove('active');
            voiceInputArea.style.display = 'block';
            textInputArea.style.display = 'none';
        });

        textModeBtn.addEventListener('click', () => {
            textModeBtn.classList.add('active');
            voiceModeBtn.classList.remove('active');
            textInputArea.style.display = 'block';
            voiceInputArea.style.display = 'none';
        });
    }
}


/**
 * Toggle between voice and text modes
 * @param {string} mode - 'voice' or 'text'
 */
function toggleMode(mode) {
    const voiceInterface = document.querySelector('.voice-interface');
    const textInterface = document.querySelector('.text-interface');
    
    if (mode === 'voice') {
        voiceInterface?.classList.remove('d-none');
        textInterface?.classList.add('d-none');
    } else if (mode === 'text') {
        voiceInterface?.classList.add('d-none');
        textInterface?.classList.remove('d-none');
    }
}

// ========================================
// RECORDING FUNCTIONALITY
// ========================================

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

/**
 * Initialize record button
 */
function initRecordButton() {
    const recordBtn = document.querySelector('.record-button');
    
    if (recordBtn) {
        recordBtn.addEventListener('click', toggleRecording);
    }
}

/**
 * Toggle recording state
 */
async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

/**
 * Start audio recording
 */
async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            await uploadAudio(audioBlob);
        };

        mediaRecorder.start();
        isRecording = true;
        updateRecordingUI(true);
        showNotification('Recording started', 'success');
    } catch (error) {
        console.error('Error accessing microphone:', error);
        showNotification('Microphone access denied', 'error');
    }
}

/**
 * Stop audio recording
 */
function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
        isRecording = false;
        updateRecordingUI(false);
        showNotification('Recording stopped', 'info');
    }
}

/**
 * Update recording button UI
 * @param {boolean} recording - Recording state
 */
function updateRecordingUI(recording) {
    const recordBtn = document.querySelector('.record-button');
    const recordIcon = recordBtn?.querySelector('i');
    
    if (recordBtn) {
        if (recording) {
            recordBtn.classList.add('recording');
            recordIcon?.classList.remove('fa-microphone');
            recordIcon?.classList.add('fa-stop');
        } else {
            recordBtn.classList.remove('recording');
            recordIcon?.classList.remove('fa-stop');
            recordIcon?.classList.add('fa-microphone');
        }
    }
}

/**
 * Upload audio to server
 * @param {Blob} audioBlob - Audio data
 */
async function uploadAudio(audioBlob) {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.wav');
    
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    try {
        const response = await fetch('/diary/upload-audio/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification('Audio uploaded successfully', 'success');
            // Refresh entries or update UI as needed
            refreshEntries();
        } else {
            showNotification('Upload failed', 'error');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showNotification('Network error', 'error');
    }
}

// ========================================
// NOTIFICATIONS
// ========================================

/**
 * Show toast notification
 * @param {string} message - Notification message
 * @param {string} type - 'success', 'error', 'info', 'warning'
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    // Add styles
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '1rem 1.5rem',
        borderRadius: '12px',
        background: getNotificationColor(type),
        color: 'white',
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease'
    });
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Get icon for notification type
 */
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        info: 'info-circle',
        warning: 'exclamation-triangle'
    };
    return icons[type] || 'info-circle';
}

/**
 * Get color for notification type
 */
function getNotificationColor(type) {
    const colors = {
        success: 'linear-gradient(135deg, #22c55e, #16a34a)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)',
        info: 'linear-gradient(135deg, #6366f1, #4f46e5)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)'
    };
    return colors[type] || colors.info;
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// ========================================
// DATA LOADING & REFRESH
// ========================================

/**
 * Refresh diary entries
 */
async function refreshEntries() {
    const entriesContainer = document.querySelector('.entries-container');
    
    if (!entriesContainer) return;
    
    try {
        const response = await fetch('/diary/entries/');
        if (response.ok) {
            const html = await response.text();
            entriesContainer.innerHTML = html;
            animateEntries();
        }
    } catch (error) {
        console.error('Error refreshing entries:', error);
    }
}

/**
 * Animate new entries
 */
function animateEntries() {
    const entries = document.querySelectorAll('.entry-card');
    entries.forEach((entry, index) => {
        entry.style.opacity = '0';
        entry.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            entry.style.transition = 'all 0.3s ease';
            entry.style.opacity = '1';
            entry.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

// ========================================
// STATS & CHARTS
// ========================================

/**
 * Initialize dashboard charts
 */
function initCharts() {
    initEntriesChart();
    initMoodChart();
}

/**
 * Initialize entries timeline chart
 */
function initEntriesChart() {
    const canvas = document.getElementById('entriesChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Entries',
                data: [3, 5, 2, 8, 6, 4, 7],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#94a3b8'
                    }
                }
            }
        }
    });
}

/**
 * Initialize mood distribution chart
 */
function initMoodChart() {
    const canvas = document.getElementById('moodChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Happy', 'Neutral', 'Sad', 'Excited'],
            datasets: [{
                data: [40, 30, 15, 15],
                backgroundColor: [
                    '#22c55e',
                    '#6366f1',
                    '#ef4444',
                    '#f59e0b'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#cbd5e1',
                        padding: 15
                    }
                }
            }
        }
    });
}

// ========================================
// SEARCH & FILTER
// ========================================

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchInput = document.querySelector('.search-input');
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
    }
}

/**
 * Handle search input
 */
function handleSearch(e) {
    const query = e.target.value.toLowerCase();
    const entries = document.querySelectorAll('.entry-card');
    
    entries.forEach(entry => {
        const text = entry.textContent.toLowerCase();
        if (text.includes(query)) {
            entry.style.display = 'block';
        } else {
            entry.style.display = 'none';
        }
    });
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ========================================
// ENTRY ACTIONS (Delete, Edit)
// ========================================

/**
 * Initialize entry action buttons
 */
function initEntryActions() {
    // Delete buttons
    document.querySelectorAll('.delete-entry').forEach(btn => {
        btn.addEventListener('click', handleDeleteEntry);
    });
    
    // Edit buttons
    document.querySelectorAll('.edit-entry').forEach(btn => {
        btn.addEventListener('click', handleEditEntry);
    });
}

/**
 * Handle entry deletion
 */
async function handleDeleteEntry(e) {
    const entryId = e.target.closest('[data-entry-id]')?.dataset.entryId;
    
    if (!entryId || !confirm('Delete this entry?')) return;
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    try {
        const response = await fetch(`/diary/entry/${entryId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        
        if (response.ok) {
            showNotification('Entry deleted', 'success');
            refreshEntries();
        } else {
            showNotification('Delete failed', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showNotification('Network error', 'error');
    }
}

/**
 * Handle entry editing
 */
function handleEditEntry(e) {
    const entryId = e.target.closest('[data-entry-id]')?.dataset.entryId;
    if (entryId) {
        window.location.href = `/diary/entry/${entryId}/edit/`;
    }
}

// ========================================
// THEME TOGGLE
// ========================================

/**
 * Initialize theme toggle
 */
function initThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        loadTheme();
    }
}

/**
 * Toggle theme
 */
function toggleTheme() {
    const currentTheme = document.body.dataset.theme || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.body.dataset.theme = newTheme;
    localStorage.setItem('theme', newTheme);
    
    updateThemeIcon(newTheme);
}

/**
 * Load saved theme
 */
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.body.dataset.theme = savedTheme;
    updateThemeIcon(savedTheme);
}

/**
 * Update theme icon
 */
function updateThemeIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// ========================================
// INITIALIZATION
// ========================================

/**
 * Initialize all dashboard features
 */
function initCharCounter() {
    const textEntry = document.getElementById('textEntry');
    const charCount = document.getElementById('charCount');

    if (textEntry && charCount) {
        textEntry.addEventListener('input', function () {
            charCount.textContent = this.value.length;
        });
    }
}

function clearTextEntry() {
    const textEntry = document.getElementById('textEntry');
    const charCount = document.getElementById('charCount');

    if (textEntry) {
        textEntry.value = '';
        if (charCount) charCount.textContent = '0';
    }
}

async function processTextEntry() {
    const textEntry = document.getElementById('textEntry');
    const content = textEntry?.value.trim();

    if (!content) {
        alert("Please write something first!");
        return;
    }

    const processBtn = document.getElementById('processTextBtn');
    processBtn.disabled = true;
    processBtn.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>Processing...`;

    try {
        const formData = new FormData(document.getElementById('textEntryForm'));
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        const response = await fetch('/diary/api/entries/text/', { 
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken },
            body: formData
        });

        if (response.ok) {
            alert("Entry saved successfully!");
            clearTextEntry();
            window.location.href = "/diary/entries/";
        } else {
            alert("Failed to save entry.");
        }
    } catch (error) {
        console.error(error);
        alert("Network error.");
    } finally {
        processBtn.disabled = false;
        processBtn.innerHTML = `<i class="fas fa-paper-plane me-2"></i>Process & Submit`;
    }
}

function initTextEntryButton() {
    const processBtn = document.getElementById('processTextBtn');
    if (processBtn) {
        processBtn.addEventListener('click', processTextEntry);
    }
}


function initDashboard() {
    initSidebar();
    setActiveNavLink();
    initModeToggle();
    initRecordButton();
    initSearch();
    initEntryActions();
    initThemeToggle();
    initCharts();

    // NEW FUNCTIONS ADDED:
    initCharCounter();
    initTextEntryButton();

    console.log('Dashboard initialized successfully');
}


// Run when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

// ========================================
// EXPORT FOR USE IN OTHER SCRIPTS
// ========================================

window.dashboardUtils = {
    showNotification,
    refreshEntries,
    toggleRecording
};
