# Drug Interaction Chatbot - Gradio Implementation

## Installation

First, install the required dependencies:

```bash
pip install gradio requests
```
## Setup Instructions

### 1. Install Ollama

```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download
```

### 2. Download a Model

```bash
# Recommended for medical queries
ollama pull llama3.2

# Alternatives
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

### 3. Start Ollama Server

```bash
# Start the server (runs on localhost:11434)
# Terminal 1
ollama serve

# Terminal 2
OLLAMA_HOST=127.0.0.1:11435 ollama serve
```

### 4. Install Python Dependencies

```bash
pip install gradio requests
```

### 5. Run the Application

```bash
# Terminal 3 (after activating .venv)
OLLAMA_MODEL="base-llama-3.1-8b-instruct-q8_0" OLLAMA_HOST_URL="http://127.0.0.1:11434" gradio drug_interaction_chatbot.py #--server-port 7860
#ollama run hf.co/MaziyarPanahi/Meta-Llama-3.1-8B-Instruct-GGUF:Q4_K_M
# Terminal 4 (after activating .venv)
GRADIO_SERVER_PORT=7861 OLLAMA_MODEL="llama3_1_8B_FT_DDI_q8" OLLAMA_HOST_URL="http://127.0.0.1:11435" gradio drug_interaction_chatbot.py #--server-port 7861
```

The application will be available at `http://localhost:7860`

## Features

### 🎯 Core Functionality
- **Smart Drug Interaction Analysis** with structured responses
- **Medical-Grade UI** with professional healthcare theme
- **Connection Testing** to verify Ollama server status
- **Conversation History** with context management
- **Error Handling** with detailed troubleshooting

### 🔧 Technical Features
- **Optimized Prompting** for medical accuracy
- **Response Formatting** with severity levels and clinical guidance
- **Timeout Handling** for large queries
- **Model Flexibility** - easily switch between GGUF models
- **Privacy-First** - all processing happens locally

### 🎨 User Experience
- **Medical Disclaimer** prominently displayed
- **Example Questions** to guide users
- **Quick Reference Guide** for effective usage
- **Responsive Design** works on all devices
- **Professional Styling** appropriate for medical context

## Customization Options

### Change the AI Model
```python
# In the chat_with_ollama function, modify:
"model": "your-preferred-model",  # e.g., "llama2", "mistral", etc.
```

### Adjust Response Parameters
```python
# Modify these values in the API call:
"temperature": 0.7,      # Higher = more creative, Lower = more focused
"max_tokens": 1500,      # Maximum response length
"top_p": 0.9,           # Nucleus sampling parameter
```

### Add Authentication
```python
# In app.launch(), add:
auth=("username", "password")
```

### Enable Public Sharing
```python
# In app.launch(), set:
share=True  # Creates a temporary public URL
```

## Troubleshooting

### Common Issues

1. **"Cannot connect to Ollama"**
   - Ensure Ollama is running: `ollama serve`
   - Check if the service is active: `curl http://localhost:11434/api/tags`

2. **"No models found"**
   - Download a model: `ollama pull llama3.2`
   - Verify installation: `ollama list`

3. **Slow responses**
   - Check system resources (RAM/CPU)
   - Try a smaller model
   - Reduce `max_tokens` parameter

4. **Port conflicts**
   - Change Gradio port: `server_port=8080`
   - Change Ollama port: `OLLAMA_HOST=0.0.0.0:11435 ollama serve`

### Performance Tips

- **For better performance:** Use quantized models (4-bit, 8-bit)
- **For accuracy:** Use larger models like `llama3.2:70b` if you have sufficient RAM
- **For speed:** Use smaller models like `llama3.2:3b`

This implementation provides a complete, production-ready drug interaction chatbot with a professional medical interface, comprehensive error handling, and optimized user experience specifically designed for pharmaceutical safety queries.