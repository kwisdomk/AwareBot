// Utility to generate a basic UUID for sessions
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// Session Management
let sessionId = localStorage.getItem('soko_session_id');
if (!sessionId) {
    sessionId = generateUUID();
    localStorage.setItem('soko_session_id', sessionId);
}

// DOM Elements
const chatContainer = document.getElementById('chat-container');
const messageList = document.getElementById('message-list');
const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const typingIndicator = document.getElementById('typing-indicator');
const stageDisplay = document.getElementById('stage-display');

// Initialize with greeting
document.addEventListener('DOMContentLoaded', () => {
    stageDisplay.textContent = 'Session Active';
    appendMessage('agent', "Welcome to Soko Akili. We help you make the best market decisions. Are you a Farmer, Seller, or Mixed?");
});

// Auto-scroll to bottom
function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// Render plain text message
function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}`;
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.textContent = text;
    
    msgDiv.appendChild(bubble);
    messageList.appendChild(msgDiv);
    scrollToBottom();
}

// Render the Agent's Decision JSON as a beautiful card
function appendDecisionCard(data) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message agent';

    let reasoningHtml = '';
    if (data.reasoning && Array.isArray(data.reasoning)) {
        reasoningHtml = `<ul>${data.reasoning.map(r => `<li>${r}</li>`).join('')}</ul>`;
    }

    const html = `
        <div class="decision-card">
            <div class="decision-header">
                <span class="decision-tag">${data.decision || 'ANALYZED'}</span>
                <span class="mode-tag">${data.mode || 'INFO'}</span>
            </div>
            
            <div class="decision-section">
                <h4>Market Context</h4>
                <p>${data.market_context || 'N/A'}</p>
            </div>

            <div class="decision-section">
                <h4>Why this decision?</h4>
                ${reasoningHtml}
            </div>

            ${data.if_wait ? `
            <div class="decision-section">
                <h4>If you wait:</h4>
                <p>${data.if_wait}</p>
            </div>
            ` : ''}

            ${data.negotiation_script ? `
            <div class="script-box">
                "${data.negotiation_script}"
            </div>
            ` : ''}
        </div>
    `;

    msgDiv.innerHTML = html;
    messageList.appendChild(msgDiv);
    scrollToBottom();
}

// Handle Form Submission
chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = messageInput.value.trim();
    if (!text) return;

    // 1. Show user message
    appendMessage('user', text);
    messageInput.value = '';
    
    // Check for restart to clear session locally
    if (text.toLowerCase() === 'restart' || text.toLowerCase() === 'anza upya') {
        sessionId = generateUUID(); // Reset local session id to force backend reset conceptually
        localStorage.setItem('soko_session_id', sessionId);
    }

    // 2. Show typing indicator
    typingIndicator.style.display = 'flex';
    messageList.appendChild(typingIndicator); // Move to bottom
    scrollToBottom();

    // 3. Send to API
    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: sessionId,
                message: text
            })
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status}`);
        }

        const data = await response.json();
        
        // Hide typing indicator
        typingIndicator.style.display = 'none';

        // Update stage display
        stageDisplay.textContent = `Stage: ${data.stage}`;

        // Render response
        if (typeof data.message === 'string') {
            appendMessage('agent', data.message);
        } else if (typeof data.message === 'object') {
            appendDecisionCard(data.message);
        }

    } catch (error) {
        typingIndicator.style.display = 'none';
        appendMessage('agent', "Sorry, I encountered a network error connecting to the market.");
        console.error(error);
    }
});
