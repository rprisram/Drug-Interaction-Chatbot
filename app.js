class DrugInteractionChatbot {
    constructor() {
        this.apiEndpoint = 'http://localhost:11434/v1/chat/completions';
        this.currentModel = 'llama3.2';
        this.messages = [];
        this.isTyping = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.checkConnection();
        this.autoResizeTextarea();
    }

    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.modelSelect = document.getElementById('modelSelect');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.connectionStatus = document.getElementById('connectionStatus');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
    }

    attachEventListeners() {
        // Send message events
        this.sendBtn.addEventListener('click', () => this.handleSendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSendMessage();
            }
        });

        // Clear chat
        this.clearBtn.addEventListener('click', () => this.clearChat());

        // Model selection
        this.modelSelect.addEventListener('change', (e) => {
            this.currentModel = e.target.value;
            this.updateConnectionStatus('connected', `Connected to ${this.currentModel}`);
        });

        // Example questions
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const question = e.target.dataset.question;
                this.messageInput.value = question;
                this.handleSendMessage();
            });
        });

        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea());
    }

    autoResizeTextarea() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }

    async checkConnection() {
        try {
            const response = await fetch(`http://localhost:11434/api/tags`);
            if (response.ok) {
                this.updateConnectionStatus('connected', `Connected to ${this.currentModel}`);
            } else {
                this.updateConnectionStatus('error', 'Connection failed');
            }
        } catch (error) {
            this.updateConnectionStatus('error', 'Ollama not running');
            console.error('Connection check failed:', error);
        }
    }

    updateConnectionStatus(status, text) {
        this.statusIndicator.className = `status-indicator ${status}`;
        this.statusText.textContent = text;
    }

    async handleSendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;

        // Clear input immediately
        this.messageInput.value = '';
        this.autoResizeTextarea();

        // Add user message to chat
        this.addMessage(message, 'user');

        // Show typing indicator
        this.showTypingIndicator();

        try {
            await this.sendToAPI(message);
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error while processing your request. Please make sure Ollama is running and try again.', 'ai', true);
            console.error('API Error:', error);
        }
    }

    addMessage(content, sender, isError = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i data-lucide="${sender === 'user' ? 'user' : 'bot'}" class="avatar-icon"></i>
            </div>
            <div class="message-content">
                <div class="message-text ${isError ? 'error-message' : ''}">${this.formatMessage(content)}</div>
                <div class="message-time">${time}</div>
            </div>
        `;

        // Remove example questions after first user message
        if (sender === 'user') {
            const exampleQuestions = document.querySelector('.example-questions');
            if (exampleQuestions) {
                exampleQuestions.style.display = 'none';
            }
        }

        this.chatMessages.appendChild(messageDiv);
        
        // Reinitialize Lucide icons for the new message
        lucide.createIcons();
        
        // Scroll to bottom
        this.scrollToBottom();
    }

    formatMessage(content) {
        // Basic formatting for better readability
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>');
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.typingIndicator.classList.add('show');
        this.sendBtn.disabled = true;
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        this.typingIndicator.classList.remove('show');
        this.sendBtn.disabled = false;
    }

    async sendToAPI(userMessage) {
        // Add system prompt for drug interaction context
        const systemPrompt = `You are a knowledgeable AI assistant specializing in drug interactions and medication safety. Provide accurate, helpful information about potential drug interactions, contraindications, and safety considerations. Always remind users to consult with healthcare professionals for personalized medical advice. Be clear about the severity of interactions (minor, moderate, major) and provide practical guidance when appropriate.`;

        // Build conversation history
        const conversationMessages = [
            { role: 'system', content: systemPrompt },
            ...this.messages,
            { role: 'user', content: userMessage }
        ];

        const requestBody = {
            model: this.currentModel,
            messages: conversationMessages,
            temperature: 0.7,
            max_tokens: 1000,
            stream: true
        };

        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Handle streaming response
            await this.handleStreamingResponse(response);

            // Add messages to conversation history
            this.messages.push({ role: 'user', content: userMessage });
            
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async handleStreamingResponse(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let aiResponse = '';
        let messageElement = null;

        this.hideTypingIndicator();

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;

                        try {
                            const parsed = JSON.parse(data);
                            const content = parsed.choices?.[0]?.delta?.content;
                            
                            if (content) {
                                aiResponse += content;
                                
                                // Create message element on first content
                                if (!messageElement) {
                                    messageElement = this.createStreamingMessage();
                                }
                                
                                // Update the message content
                                this.updateStreamingMessage(messageElement, aiResponse);
                            }
                        } catch (e) {
                            // Skip invalid JSON lines
                            continue;
                        }
                    }
                }
            }

            // Add to conversation history
            if (aiResponse.trim()) {
                this.messages.push({ role: 'assistant', content: aiResponse });
            }

        } catch (error) {
            console.error('Streaming error:', error);
            throw error;
        }
    }

    createStreamingMessage() {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message ai-message';
        
        const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i data-lucide="bot" class="avatar-icon"></i>
            </div>
            <div class="message-content">
                <div class="message-text streaming-text"></div>
                <div class="message-time">${time}</div>
            </div>
        `;

        this.chatMessages.appendChild(messageDiv);
        lucide.createIcons();
        
        return messageDiv;
    }

    updateStreamingMessage(messageElement, content) {
        const textElement = messageElement.querySelector('.message-text');
        textElement.innerHTML = this.formatMessage(content);
        this.scrollToBottom();
    }

    clearChat() {
        // Remove all user and AI messages except welcome message, examples, and disclaimer
        const messages = this.chatMessages.querySelectorAll('.message:not(.message:first-child)');
        messages.forEach(message => message.remove());
        
        // Show example questions again
        const exampleQuestions = document.querySelector('.example-questions');
        if (exampleQuestions) {
            exampleQuestions.style.display = 'block';
        }
        
        // Clear conversation history
        this.messages = [];
        
        // Reset input
        this.messageInput.value = '';
        this.autoResizeTextarea();
        
        this.scrollToBottom();
    }

    scrollToBottom() {
        requestAnimationFrame(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        });
    }
}

// Initialize the chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Prevent multiple initializations
    if (!window.chatbotInitialized) {
        window.chatbot = new DrugInteractionChatbot();
        window.chatbotInitialized = true;
    }
});

// Handle page visibility for connection checking
document.addEventListener('visibilitychange', () => {
    if (!document.hidden && window.chatbot) {
        window.chatbot.checkConnection();
    }
});