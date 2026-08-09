// ========================================
// AI INTERVIEW AGENT - FRONTEND LOGIC
// ========================================

const API_URL = 'http://localhost:8000/api/interview';
let sessionId = 'session-' + Date.now();
let questionCount = 0;
const MAX_QUESTIONS = 8;
let isLoading = false;
let coveredDays = new Set();
let interviewActive = false;

// ===== ALL CANDIDATES DATA =====
const ALL_CANDIDATES = {
    'CAND-001': { id: 'CAND-001', name: 'Sarah Johnson', jobRole: 'Senior Data Engineer', yearsExperience: 9, education: 'MS Computer Science', status: 'COMPLETED' },
    'CAND-002': { id: 'CAND-002', name: 'Alex Turner', jobRole: 'Backend Software Engineer', yearsExperience: 5, education: 'B.Tech Computer Science', status: 'COMPLETED' },
    'CAND-003': { id: 'CAND-003', name: 'Emily Chen', jobRole: 'AI Engineer', yearsExperience: 6, education: 'MS Artificial Intelligence', status: 'COMPLETED' },
    'CAND-004': { id: 'CAND-004', name: 'David Miller', jobRole: 'Business Analyst', yearsExperience: 8, education: 'MBA', status: 'COMPLETED' },
    'CAND-005': { id: 'CAND-005', name: 'Michael Brown', jobRole: 'DevOps Engineer', yearsExperience: 10, education: 'B.Tech Information Technology', status: 'COMPLETED' },
    'CAND-006': { id: 'CAND-006', name: 'Wendy Foster', jobRole: 'Marketing Manager', yearsExperience: 12, education: 'BA Marketing', status: 'COMPLETED' },
    'CAND-007': { id: 'CAND-007', name: 'Ethan Brooks', jobRole: 'Computer Science Intern', yearsExperience: 0, education: 'BS Computer Science (in progress)', status: 'COMPLETED' },
    'CAND-008': { id: 'CAND-008', name: 'Harold Whitfield', jobRole: 'Distinguished Engineer', yearsExperience: 28, education: 'BS Computer Science', status: 'COMPLETED' },
    'CAND-009': { id: 'CAND-009', name: 'Zara Ahmadi', jobRole: 'AI Engineer', yearsExperience: 1, education: 'BS Computer Science', status: 'COMPLETED' },
    'CAND-010': { id: 'CAND-010', name: 'Gerald Combs', jobRole: 'IT Support Specialist', yearsExperience: 20, education: 'AAS Information Technology', status: 'COMPLETED' },
    'CAND-011': { id: 'CAND-011', name: 'Mia Alvarez', jobRole: 'UX Researcher', yearsExperience: 6, education: 'MA Human-Computer Interaction', status: 'COMPLETED' },
    'CAND-012': { id: 'CAND-012', name: 'Chen Wei', jobRole: 'Mobile App Developer', yearsExperience: 7, education: 'BS Computer Engineering', status: 'COMPLETED' },
    'CAND-013': { id: 'CAND-013', name: 'Ravi Patel', jobRole: 'Software Engineer', yearsExperience: 15, education: 'MS Computer Science', status: 'COMPLETED' },
    'CAND-014': { id: 'CAND-014', name: 'Bethany Cole', jobRole: 'HR Manager', yearsExperience: 10, education: 'BA Human Resources', status: 'COMPLETED' },
    'CAND-015': { id: 'CAND-015', name: 'Noah Kim', jobRole: 'Principal Architect', yearsExperience: 20, education: 'MS Computer Science', status: 'COMPLETED' },
    'CAND-016': { id: 'CAND-016', name: 'Isabella Rossi', jobRole: 'Software Engineer', yearsExperience: 5, education: 'BS Computer Science', status: 'COMPLETED' },
    'CAND-017': { id: 'CAND-017', name: 'Tyler Brooks', jobRole: 'Junior Developer', yearsExperience: 0, education: 'GED + Coding Bootcamp Certificate', status: 'COMPLETED' },
    'CAND-018': { id: 'CAND-018', name: 'Diane Foster', jobRole: 'AI Engineer', yearsExperience: 4, education: 'MS Computer Science', status: 'COMPLETED' },
    'CAND-019': { id: 'CAND-019', name: 'Frank DeLuca', jobRole: 'Legacy Systems Engineer', yearsExperience: 25, education: 'BS Computer Science', status: 'COMPLETED' },
    'CAND-020': { id: 'CAND-020', name: 'Priyanka Sharma', jobRole: 'Software Engineer', yearsExperience: 5, education: 'BS Computer Science', status: 'COMPLETED' }
};

// ===== DOM ELEMENTS =====
const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const questionCounter = document.getElementById('questionCounter');
const feedbackOverlay = document.getElementById('feedbackOverlay');
const feedbackBody = document.getElementById('feedbackBody');
const candidateSelect = document.getElementById('candidateSelect');
const startNewBtn = document.getElementById('startNewBtn');
const endInterviewBtn = document.getElementById('endInterviewBtn');
const dayCount = document.getElementById('dayCount');
const statusText = document.getElementById('statusText');

// ===== FORCE SCROLL FUNCTION =====
function scrollToBottom() {
    // Try multiple ways to ensure scrolling works
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
        // Backup: scroll the whole window if needed
        window.scrollTo(0, document.body.scrollHeight);
    }
    console.log('🔄 Scrolled to bottom'); // Debug log
}

// ===== POPULATE CANDIDATES =====
for (const [id, data] of Object.entries(ALL_CANDIDATES)) {
    const option = document.createElement('option');
    option.value = id;
    option.textContent = `${data.name} - ${data.jobRole}`;
    candidateSelect.appendChild(option);
}

// ===== HELPER FUNCTIONS =====
function getSelectedCandidate() {
    const id = candidateSelect.value;
    return ALL_CANDIDATES[id] || ALL_CANDIDATES['CAND-001'];
}

function addMessage(sender, text) {
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const div = document.createElement('div');
    div.className = `message ${sender.toLowerCase()}`;
    div.innerHTML = `
        <span class="sender">${sender === 'AI' ? '🤖 Interviewer' : '👤 You'}</span>
        ${text}
    `;
    chatMessages.appendChild(div);
    
    // 🔥 SCROLL AFTER ADDING MESSAGE
    scrollToBottom();
}

function showTyping() {
    const existing = document.querySelector('.typing-indicator');
    if (existing) existing.remove();

    const div = document.createElement('div');
    div.className = 'typing-indicator';
    div.id = 'typingIndicator';
    div.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    chatMessages.appendChild(div);
    
    // 🔥 SCROLL AFTER SHOWING TYPING
    scrollToBottom();
}

function hideTyping() {
    const el = document.getElementById('typingIndicator');
    if (el) {
        el.remove();
        // 🔥 SCROLL AFTER REMOVING TYPING
        scrollToBottom();
    }
}

function updateProgress(questionNumber) {
    questionCount = questionNumber;
    const percentage = Math.min((questionNumber / MAX_QUESTIONS) * 100, 100);
    progressFill.style.width = percentage + '%';
    progressText.textContent = `${questionNumber} / ${MAX_QUESTIONS}`;
    questionCounter.textContent = `Question ${questionNumber} of ${MAX_QUESTIONS}`;
}

function updateDayTracker() {
    dayCount.textContent = coveredDays.size;
    if (coveredDays.size >= 4) {
        statusText.textContent = '✅ Complete';
        statusText.style.color = '#2e7d32';
    } else {
        statusText.textContent = `${coveredDays.size}/4 days`;
        statusText.style.color = '#4a5568';
    }
}

function setLoading(loading) {
    isLoading = loading;
    messageInput.disabled = loading;
    sendBtn.disabled = loading;
    endInterviewBtn.disabled = loading || !interviewActive;
    sendBtn.innerHTML = loading
        ? '<span>Thinking...</span>'
        : '<span>Send</span><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>';
}

function setInterviewActive(active) {
    interviewActive = active;
    endInterviewBtn.disabled = !active;
    statusText.textContent = active ? '🟢 Live' : 'Ready';
    statusText.style.color = active ? '#2e7d32' : '#4a5568';
}

function resetInterview() {
    questionCount = 0;
    coveredDays = new Set();
    updateProgress(0);
    updateDayTracker();
    chatMessages.innerHTML = '';
    const welcome = document.createElement('div');
    welcome.className = 'welcome-message';
    welcome.innerHTML = `
        <div class="welcome-icon">🤖</div>
        <h3>Ready to Begin</h3>
        <p>Select a candidate and start the interview. The AI will adapt questions based on their learning journey.</p>
    `;
    chatMessages.appendChild(welcome);
    setInterviewActive(false);
    messageInput.disabled = true;
    sendBtn.disabled = true;
}

function extractDayFromText(text) {
    const patterns = [
        /(?:^|\s)Day\s*(\d+)/i,
        /(?:^|\s)day\s*(\d+)/i,
        /(?:^|\s)on\s*day\s*(\d+)/i
    ];
    for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match) {
            const dayNum = parseInt(match[1]);
            if (dayNum >= 1 && dayNum <= 31) return dayNum;
        }
    }
    return null;
}

// ===== API CALLS =====
async function startInterview() {
    const candidate = getSelectedCandidate();
    sessionId = 'session-' + Date.now();
    resetInterview();
    
    setLoading(true);
    showTyping();
    setInterviewActive(true);

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: sessionId,
                candidate: candidate
            })
        });

        const data = await response.json();
        hideTyping();
        addMessage('AI', data.reply);
        updateProgress(1);
        
        const day = extractDayFromText(data.reply);
        if (day) {
            coveredDays.add(day);
            updateDayTracker();
        }
        
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    } catch (error) {
        hideTyping();
        addMessage('AI', '⚠️ Unable to connect to the interview server.');
        console.error('Start error:', error);
        setInterviewActive(false);
    } finally {
        setLoading(false);
    }
}

async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isLoading || !interviewActive) return;

    messageInput.value = '';
    addMessage('You', message);
    setLoading(true);
    showTyping();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: sessionId,
                message: message
            })
        });

        const data = await response.json();
        hideTyping();
        addMessage('AI', data.reply);

        const day = extractDayFromText(data.reply);
        if (day) {
            coveredDays.add(day);
            updateDayTracker();
        }

        const nextQuestion = questionCount + 1;
        updateProgress(nextQuestion);

        if (data.done && data.feedback) {
            showFeedback(data.feedback);
            messageInput.disabled = true;
            sendBtn.disabled = true;
            setInterviewActive(false);
            celebrate();
        } else {
            messageInput.focus();
        }
    } catch (error) {
        hideTyping();
        addMessage('AI', '⚠️ Error sending your message.');
        console.error('Send error:', error);
    } finally {
        setLoading(false);
    }
}

async function endInterview() {
    if (!interviewActive || isLoading) return;
    if (!confirm('End the interview and get feedback?')) return;
    
    setLoading(true);
    showTyping();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                sessionId: sessionId,
                message: "END_INTERVIEW"
            })
        });

        const data = await response.json();
        hideTyping();
        
        if (data.done && data.feedback) {
            addMessage('AI', '📋 Interview ended. Generating feedback...');
            showFeedback(data.feedback);
            setInterviewActive(false);
            messageInput.disabled = true;
            sendBtn.disabled = true;
            celebrate();
        } else {
            addMessage('AI', data.reply || 'Interview ended.');
            setInterviewActive(false);
        }
    } catch (error) {
        hideTyping();
        addMessage('AI', '⚠️ Error ending interview.');
        console.error('End error:', error);
    } finally {
        setLoading(false);
    }
}

// ===== FEEDBACK =====
function showFeedback(feedback) {
    feedbackBody.innerHTML = `
        <h3>📝 Summary</h3>
        <p>${feedback.summary || 'No summary available.'}</p>

        <h3>✅ Strengths</h3>
        <ul>${(feedback.strengths || []).map(s => `<li>${s}</li>`).join('')}</ul>

        <h3>⚡ Areas for Growth</h3>
        <ul>${(feedback.gaps || []).map(g => `<li>${g}</li>`).join('')}</ul>

        <h3>🚀 Recommended Next Steps</h3>
        <ul>${(feedback.next || []).map(n => `<li>${n}</li>`).join('')}</ul>
        
        <div class="feedback-actions">
            <button onclick="downloadReport()" class="btn-primary">📥 Download Report</button>
            <button onclick="closeFeedback()" class="btn-secondary">Close</button>
        </div>
    `;
    feedbackOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeFeedback() {
    feedbackOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

function downloadReport() {
    const candidate = getSelectedCandidate();
    const content = `
==========================================
        AI INTERVIEW REPORT
==========================================

Candidate: ${candidate.name}
Role: ${candidate.jobRole}
Date: ${new Date().toLocaleString()}
Questions: ${questionCount}
Days Covered: ${coveredDays.size} - ${Array.from(coveredDays).sort((a,b)=>a-b).join(', ')}

==========================================
FEEDBACK
==========================================

${feedbackBody.innerText}

==========================================
    Report generated by AI Interview Agent
==========================================
    `;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `interview-report-${candidate.name}-${Date.now()}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// ===== CONFETTI CELEBRATION =====
function celebrate() {
    const colors = ['#4a6cf7', '#6a4cf7', '#4caf50', '#ff6b6b', '#ffd93d'];
    for (let i = 0; i < 60; i++) {
        setTimeout(() => {
            const el = document.createElement('div');
            const size = 6 + Math.random() * 8;
            el.style.cssText = `
                position: fixed;
                width: ${size}px;
                height: ${size}px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                left: ${Math.random() * 100}vw;
                top: -20px;
                border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
                pointer-events: none;
                z-index: 9999;
                animation: confettiFall ${2 + Math.random() * 2}s linear forwards;
            `;
            document.body.appendChild(el);
            setTimeout(() => el.remove(), 4000);
        }, i * 30);
    }
}

// ===== INJECT CONFETTI STYLES =====
const style = document.createElement('style');
style.textContent = `
    @keyframes confettiFall {
        0% { transform: translateY(0) rotate(0deg) scale(1); opacity: 1; }
        100% { transform: translateY(100vh) rotate(720deg) scale(0.2); opacity: 0; }
    }
`;
document.head.appendChild(style);

// ===== EVENT LISTENERS =====
sendBtn.addEventListener('click', sendMessage);
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});
startNewBtn.addEventListener('click', startInterview);
endInterviewBtn.addEventListener('click', endInterview);

feedbackOverlay.addEventListener('click', (e) => {
    if (e.target === feedbackOverlay) closeFeedback();
});

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeFeedback();
    if (e.ctrlKey && e.key === 'n') { e.preventDefault(); startInterview(); }
    if (e.ctrlKey && e.key === 'e') { e.preventDefault(); endInterview(); }
});

// ===== START THE INTERVIEW =====
document.addEventListener('DOMContentLoaded', startInterview);