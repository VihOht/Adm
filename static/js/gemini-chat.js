// Gemini Chat Functionality
let chatMessages = [];

function handleEnterKey(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (message === '') return;
    
    // Add user message
    addMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Awaits AI response
    generateResponse(message);
}

function addMessage(message, sender) {
    const chatContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = sender === 'user' ? 'chat chat-end' : 'chat chat-start';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = sender === 'user' ? 'chat-bubble chat-bubble-secondary' : 'chat-bubble chat-bubble-primary';
    bubbleDiv.textContent = message;
    
    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    // Store message
    chatMessages.push({ message, sender, timestamp: new Date() });
}

function showTypingIndicator() {
    const chatContainer = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'chat chat-start';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'chat-bubble chat-bubble-primary typing-indicator';
    bubbleDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    bubbleDiv.style.display = 'flex';
    
    typingDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function generateResponse(userMessage) {

    data = {'user_message': userMessage}
    try {
      const response = await fetch(`/ai/get_response/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      if (result.success){
        if (typeof toastSuccess !== 'undefined') {
          toastSuccess(result.message)
        } else {
          console.log(result.message)
        }
        addMessage(result.ai_response, 'ai')
        hideTypingIndicator()
      }
      else {
        if (typeof toastError !== 'undefined') {
          toastError(result.message)
        } else {
          console.log(result.message)
        }
        hideTypingIndicator()
      }
  
  }
    catch (exception) {
      if (typeof toastError !== 'undefined') {
        toastError('Error ${exception}')
      } else {
        console.log(exception)
      }
      console.log(exception)
      hideTypingIndicator()
    }
}

async function generateFloatingResponse(userMessage) {
    data = {'user_message': userMessage}
    try {
      const response = await fetch(`/ai/get_response/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      if (result.success){
        if (typeof toastSuccess !== 'undefined') {
          toastSuccess(result.message)
        } else {
          console.log(result.message)
        }
        addFloatingMessage(result.ai_response, 'ai')
        hideFloatingTypingIndicator()
      }
      else {
        if (typeof toastError !== 'undefined') {
          toastError(result.message)
        } else {
          console.log(result.message)
        }
        hideFloatingTypingIndicator()
      }
  
  }
    catch (exception) {
      if (typeof toastError !== 'undefined') {
        toastError('Error ${exception}')
      } else {
        console.log(exception)
      }
      console.log(exception)
      hideFloatingTypingIndicator()
    }
}

// Floating Chat Widget Functionality
function toggleFloatingChat() {
    const chatWindow = document.getElementById('floating-chat-window');
    const isVisible = chatWindow.style.display === 'flex';
    
    if (isVisible) {
        chatWindow.style.display = 'none';
    } else {
        chatWindow.style.display = 'flex';
        // Focus on input when opening
        setTimeout(() => {
            const input = document.getElementById('floating-chat-input');
            if (input) input.focus();
        }, 100);
    }
}

function closeFloatingChat() {
    document.getElementById('floating-chat-window').style.display = 'none';
}

function sendFloatingMessage() {
    const input = document.getElementById('floating-chat-input');
    const message = input.value.trim();
    
    if (message === '') return;
    
    // Add user message to floating chat
    addFloatingMessage(message, 'user');
    input.value = '';
    
    // Show typing indicator in floating chat
    showFloatingTypingIndicator();
    
    // Use the same generateResponse function but for floating chat
    generateFloatingResponse(message);
}

function addFloatingMessage(message, sender) {
    const chatContainer = document.getElementById('floating-chat-messages');
    const messageDiv = document.createElement('div');
    
    messageDiv.className = sender === 'user' ? 'chat chat-end' : 'chat chat-start';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = sender === 'user' ? 'chat-bubble chat-bubble-secondary' : 'chat-bubble chat-bubble-primary';
    bubbleDiv.textContent = message;
    
    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);
    
    // Scroll to bottom
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showFloatingTypingIndicator() {
    const chatContainer = document.getElementById('floating-chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'floating-typing-indicator';
    typingDiv.className = 'chat chat-start';
    
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'chat-bubble chat-bubble-primary typing-indicator';
    bubbleDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    bubbleDiv.style.display = 'flex';
    
    typingDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideFloatingTypingIndicator() {
    const typingIndicator = document.getElementById('floating-typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function handleFloatingEnterKey(event) {
    if (event.key === 'Enter') {
        sendFloatingMessage();
    }
}

// Utility for getting the CSRFToken
function getCSRFToken() {
  // First try to get from window (set in template)
  if (window.csrfToken) {
    return window.csrfToken;
  }
  
  // Fallback to hidden input
  const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (csrfInput) {
    return csrfInput.value;
  }
  
  // Fallback to cookie
  return getCookie('csrftoken');
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Initialize floating chat when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add floating chat widget to the page if it doesn't exist
    if (!document.getElementById('floating-chat-widget')) {
        const floatingChatHTML = `
            <div id="floating-chat-widget" class="floating-chat-widget">
                <button class="chat-toggle-btn" onclick="toggleFloatingChat()">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 2L2 7v10c0 5.55 4.45 10 10 10s10-4.45 10-10V7l-10-5z"/>
                        <path d="M12 17l-5-3V9l5-3 5 3v5l-5 3z"/>
                    </svg>
                </button>
                
                <div id="floating-chat-window" class="floating-chat-window">
                    <div class="floating-chat-header">
                        <div>
                            <h3 style="margin: 0; font-size: 16px;">Gemini AI</h3>
                            <p style="margin: 0; font-size: 12px; opacity: 0.8;">Online</p>
                        </div>
                        <button onclick="closeFloatingChat()" style="background: none; border: none; color: white; cursor: pointer;">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18"></line>
                                <line x1="6" y1="6" x2="18" y2="18"></line>
                            </svg>
                        </button>
                    </div>
                    
                    <div id="floating-chat-messages" class="floating-chat-messages">
                        <div class="chat chat-start">
                            <div class="chat-bubble chat-bubble-primary">
                                Hi! I'm your Gemini AI assistant. How can I help you today?
                            </div>
                        </div>
                    </div>
                    
                    <div class="floating-chat-input-container">
                        <input 
                            type="text" 
                            id="floating-chat-input" 
                            placeholder="Type a message..." 
                            class="floating-chat-input"
                            onkeypress="handleFloatingEnterKey(event)"
                        >
                        <button class="floating-chat-send-btn" onclick="sendFloatingMessage()">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="22" y1="2" x2="11" y2="13"></line>
                                <polygon points="22,2 15,22 11,13 2,9 22,2"></polygon>
                            </svg>
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', floatingChatHTML);
    }
});
