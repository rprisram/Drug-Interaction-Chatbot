import gradio as gr
import requests
import json
import time
import os

#OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", 'llama3.1:8b')
#OLLAMA_HOST_URL = os.getenv("OLLAMA_HOST_URL","http://localhost:11434")
BACKEND_API_URL = os.environ.get('BACKEND_API_URL')
print(f"--- Frontend starting. Backend API URL from env: {BACKEND_API_URL} ---")


BACKEND_HEALTH_URL = f"{BACKEND_API_URL}/health" if BACKEND_API_URL else None
BACKEND_CHAT_URL = f"{BACKEND_API_URL}/chat" if BACKEND_API_URL else None

def chat_with_backend(message, history):
    """Calls our FastAPI backend, which in turn calls Vertex AI."""
    try:
        payload = {"message": message, "history": history}
        response = requests.post(f"{BACKEND_CHAT_URL}", json=payload,timeout = 65)
        response.raise_for_status()
        data = response.json()
        return data.get("response", data.get("error", "An unknown error occurred."))
    except Exception as e:
        return f"** Connection Error:** Cannot connect to backend API, details: {str(e)}"

def check_backend_connection():
    """Tests the connection to our FastAPI backend."""
    try:
        response = requests.get(f"{BACKEND_HEALTH_URL}", timeout=15)
        return " ** Connected to Backend API!! Ready to Analyze." if response.status_code == 200 else f" **Backend API Warning:** Status {response.status_code}"
    except requests.exceptions.RequestException as e:
        return f"{str(e)}** Cannot connect to backend API.** Please start it: `uvicorn main:app --reload`"

'''def chat_with_ollama(message, history):
    """
    Main chat function that interfaces with Ollama API for drug interaction queries
    """
    
    # Enhanced system prompt specifically for drug interactions
    system_prompt = """You are a knowledgeable medical AI assistant specializing in drug interactions and pharmaceutical safety.

Formatting Rules (must follow exactly):
- Always answer using the following sections in this order and with these exact headings.
- If a field is unknown, write "N/A" rather than omitting the section.
- Do not add sections that are not listed.
- Keep language concise and clinically neutral.
- End with the disclaimer line.

Template (fill every section):
🔍 Drug Interaction Analysis

Interaction Severity: [None/Minor/Moderate/Major/Contraindicated]
Mechanism: [concise mechanism]
Clinical Effects: [concise bullet or short sentence list]
Risk Factors: [concise bullet or short sentence list]
Management: [specific actions: avoid/combine with caution/monitor; include what to monitor]
Evidence Level: [Strong/Moderate/Limited]

Important: This is for educational purposes only and is not a substitute for professional medical advice. Consult a healthcare professional for decisions.

Behavior:
- If the query is not about drugs or interactions, briefly redirect and ask for a drug-related question, still using the same template (fill with "N/A" where appropriate).
"""
    
    # Prepare messages for Ollama API
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history (limited to last 10 exchanges to manage context)
    recent_history = history[-20:] if history else []
    for turn in recent_history:
        role = turn.get("role")
        content = turn.get("content", "")
        if role in {"user", "system"} and content:
            messages.append({"role": role, "content": content})
        elif role in {"assistant"} and content:
            clean_content = content.split("--- *Ollama API")[0].strip()
            messages.append({"role": role, "content": clean_content})
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    try:
        # Call Ollama API with error handling and retries
        start = time.time()
        response = requests.post(
            f"{OLLAMA_HOST_URL}/v1/chat/completions",
            json={
                "model": OLLAMA_MODEL,  # You can change this to your preferred model
                "messages": messages,
                "temperature": 0.2,  # Balanced creativity vs accuracy
                "max_tokens": 1500,  # Sufficient for detailed medical responses
                "stream": False,
                "top_p": 0.9,
                "frequency_penalty": 0.1
            },
            headers={"Content-Type": "application/json"},
            timeout=60  # Extended timeout for medical queries
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # Add timestamp and source attribution
            end = time.time()
            elapsed = end - start
            timestamp = time.strftime("%H:%M", time.localtime())
            #attributed_response = f"{ai_response}\n\n---\n*Response generated at {timestamp} using Ollama AI*"
            attributed_response = f"{ai_response}\n\n--- *Ollama API • {OLLAMA_MODEL} • {timestamp} • {elapsed:.1f}s* ---"
            return attributed_response
        else:
            return f"❌ **API Error:** Unable to connect to Ollama (Status: {response.status_code})\n\nPlease ensure:\n- Ollama is running (`ollama serve`)\n- The model is available (`ollama pull llama3.2`)\n- Port 11434 is accessible"
            
    except requests.exceptions.ConnectionError:
        return "❌ **Connection Error:** Cannot connect to Ollama server.\n\n**Troubleshooting:**\n- Start Ollama: `ollama serve`\n- Check if running: `curl http://localhost:11434/api/tags`\n- Verify model: `ollama list`"
    except requests.exceptions.Timeout:
        return "⏱️ **Timeout Error:** The AI took too long to respond. Please try a shorter question or check your system resources."
    except Exception as e:
        return f"❌ **Unexpected Error:** {str(e)}\n\nPlease try again or check the console for detailed error information."

def check_ollama_connection():
    """
    Test function to check Ollama connection and available models
    """
    try:
        # Test basic connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            if models:
                return f"✅ **Connected!** Available models: {', '.join(models)}"
            else:
                return "⚠️ **Connected but no models found.** Run: `ollama pull llama3.2`"
        else:
            return f"❌ Connection failed (Status: {response.status_code})"
    except:
        return "❌ **Cannot connect to Ollama.** Please start with: `ollama serve`"
'''
def create_drug_interaction_chatbot():
    """
    Create the complete Gradio interface for the drug interaction chatbot
    """
    
    # Custom CSS for medical theme
    custom_css = """
    /* --- 1. GENERAL LAYOUT & THEME DEFAULTS --- */
    .gradio-container {
        max-width: 900px !important;
        margin: auto !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Default text color for the app will follow the theme (light on dark, dark on light) */
    body, .gradio-container {
        color: var(--body-text-color);
    }

    /* Make the header theme-aware, as it sits on the main background */
    .header-title, .header-title h1, .header-title h3, .header-title p {
        text-align: center;
        color: var(--body-text-color); /* This makes it adapt to the theme */
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .header-title h3 {
        color: var(--body-text-color-subdued); /* Use a subdued color for subtitles */
    }


    /* --- 2. CUSTOM COMPONENTS WITH LIGHT BACKGROUNDS --- */
    /* For these specific components, we ALWAYS want dark text, regardless of the theme. */
    .disclaimer, .feature-box, .connection-status, .example-item, .footer-note {
        color: #1f2937 !important; /* slate-800 for readability */
    }
    /* This powerful rule ensures ALL child elements (p, h3, strong, etc.) inside these
    light boxes also get the same dark text color, avoiding specificity conflicts. */
    .disclaimer *, .feature-box *, .connection-status *, .example-item *, .footer-note * {
        color: inherit !important; /* Inherit the dark color from the parent */
    }

    .disclaimer {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 2px solid #f39c12;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .disclaimer h3 {
        color: #d68910 !important; /* Keep the special orange color for the heading */
        margin-top: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .feature-box {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border: 1px solid #28a745;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    .connection-status {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        border-left: 4px solid #007bff;
    }

    /* --- 3. INTERACTIVE ELEMENTS --- */
    .example-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 10px;
        margin: 15px 0;
    }
    .example-item {
        background: #f1f3f4;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        cursor: pointer;
        transition: all 0.2s;
    }
    .example-item:hover {
        background: #e9ecef;
        border-color: #007bff;
        transform: translateY(-1px);
    }


    /* --- 4. CHATBOT STYLES --- */
    .chat-container {
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        overflow: hidden;
    }

    /* Define chatbot bubble colors that work well in dark mode */
    .gr-chatbot .message.bot {
        background: #27272a;  /* A nice dark gray for bot bubble */
        color: #f4f4f5 !important; /* Light gray text */
    }
    .gr-chatbot .message.user {
        background: #007bff;  /* Blue for user bubble */
        color: white !important;
    }
    """
    
    with gr.Blocks(
        title="🏥 Drug Interaction Chatbot - Powered by Vertex AI",
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="green",
            neutral_hue="slate"
        ),
        css=custom_css
    ) as demo:
        
        # Header
        gr.HTML("""
        <div class="header-title">
            <h1>🏥 Drug Interaction Chatbot</h1>
            <h3>🤖 Powered by Model in Google Vertex AI</h3>
            <p><em>Intelligent pharmaceutical safety analysis at your fingertips</em></p>
        </div>
        """)
        
        # Medical Disclaimer
        gr.HTML("""
        <div class="disclaimer">
            <h3>⚠️ Important Medical Disclaimer</h3>
            <p><strong>This chatbot provides general educational information only and is NOT a substitute for professional medical advice.</strong></p>
            <ul>
                <li>Always consult your healthcare provider before making medication decisions</li>
                <li>Do not stop or change medications without medical supervision</li>
                <li>Seek immediate medical attention for drug allergies or adverse reactions</li>
                <li>This tool does not replace pharmacist or physician consultation</li>
            </ul>
        </div>
        """)
        
        # Connection Status and Test
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML('<div class="connection-status"><h4>🔌 Backend API Connection Status</h4></div>')
            with gr.Column(scale=1):
                test_btn = gr.Button("🔍 Test Connection", variant="secondary")
                
        connection_output = gr.Textbox(
            label="Connection Status",
            value="Click 'Test Connection' to verify Backend API is running...",
            interactive=False,
            max_lines=3
        )
        
        # Features Overview
        gr.HTML("""
        <div class="feature-box">
            <h4>✨ What I Can Help With:</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px;">
                <div>
                    <strong>🔬 Drug Interactions:</strong><br>
                    Analyze potential interactions between medications
                </div>
                <div>
                    <strong>⚡ Side Effects:</strong><br>
                    Information about medication side effects
                </div>
                <div>
                    <strong>🎯 Contraindications:</strong><br>
                    Identify when drugs should not be used together
                </div>
                <div>
                    <strong>📋 Safety Guidelines:</strong><br>
                    Dosage considerations and monitoring recommendations
                </div>
            </div>
        </div>
        """)
        
        # Main Chat Interface
        gr.HTML('<div class="chat-container">')
        
        chatbot = gr.ChatInterface(
            type="messages",
            fn=chat_with_backend,
            title="💬 Ask About Drug Interactions",
            description="Type your questions about medication interactions, side effects, or drug safety below.",
            show_progress='minimal',
            examples=[
                "Can I take aspirin with warfarin? What are the risks?",
                "What happens if I mix alcohol with metformin?",
                "Is it safe to take ibuprofen with lisinopril for blood pressure?",
                "Can I take acetaminophen while on sertraline antidepressant?",
                "Do antibiotics like amoxicillin affect birth control effectiveness?",
                "What are the interactions between atorvastatin and grapefruit?",
                "Can I take omeprazole with clopidogrel safely?",
                "Are there any issues with taking vitamin supplements and blood thinners?"
            ],
            #retry_btn="🔄 Retry Analysis",
            #undo_btn="↩️ Undo Last",
            #clear_btn="🗑️ Clear Conversation",
            submit_btn="🔍 Analyze Interaction",
            textbox=gr.Textbox(
                placeholder="Example: 'Can I take medication X with medication Y?' or 'What are the side effects of combining drug A and drug B?'",
                container=False,
                scale=7
            ),
            chatbot=gr.Chatbot(
                type="messages",
                height=500,
                placeholder="<div style='text-align: center; color: #666;'><h3>🏥 Welcome to Drug Interaction Analysis</h3><p>Start by asking about any medication interactions you'd like to understand better.</p><p><em>Remember: This is for educational purposes only!</em></p></div>",
                #bubble_full_width=False,
                show_label=False
            )
        )
        
        gr.HTML('</div>')
        
        # Quick Reference Guide
        with gr.Accordion("📚 Quick Reference Guide", open=False):
            gr.Markdown("""
            ### How to Ask Effective Questions:
            
            **✅ Good Examples:**
            - "What are the interactions between [Drug A] and [Drug B]?"
            - "Can I take [medication] with [condition/other medication]?"
            - "What should I monitor when taking [drug combination]?"
            - "Are there alternatives to [drug] that don't interact with [other drug]?"
            
            **❌ Avoid:**
            - Personal medical history details
            - Requests for specific medical advice
            - Dosage recommendations for your specific situation
            
            ### Interaction Severity Levels:
            - **None:** No significant interaction expected
            - **Minor:** Minimal clinical significance
            - **Moderate:** May require monitoring or dose adjustment
            - **Major:** Significant risk, alternative therapy recommended
            - **Contraindicated:** Do not use together
            
            ### When to Seek Professional Help:
            - Any concerning symptoms after taking medications
            - Questions about your specific dosages
            - Pregnancy or breastfeeding considerations
            - Complex medical conditions
            """)
        
        # Technical Information
        with gr.Accordion("⚙️ Technical Information", open=False):
            gr.Markdown("""
            ### System Information:
            - **AI Model:** Fine-tuned Llama 3.1 hosted on Google Vertex AI
            - **API Endpoint:** http://<Google Cloud Run Endpoint>/chat (Application Backend)
            - **Processing:** UI calls a secure backend, which calls Vertex AI.
            """)
        
        # Footer
        gr.HTML("""
        <div style="text-align: center; margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 10px;" class ='footer-note'>
            <p><strong>🏥 Drug Interaction Chatbot v1.0</strong></p>
            <p>Built with ❤️ using Gradio & Ollama | For Educational Purposes Only</p>
            <p><em>Always consult healthcare professionals for medical decisions</em></p>
        </div>
        """)
        
        # Connect the test button
        test_btn.click(
            fn=check_backend_connection,
            outputs=connection_output
        )
    
    return demo

demo = create_drug_interaction_chatbot()
# Launch the application
if __name__ == "__main__":
    print("🏥 Starting Drug Interaction Chatbot...")
    print("📋 Loading Gradio interface...")
    
    print("✅ Application ready!")
    # Launch with optimized settings
    demo.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port = int(os.environ.get('PORT', 8080)),
       # server_port=7860,       # Standard Gradio port
        share=False,            # Set to True for public sharing
        debug=False,            # Set to True for development
        show_error=True,        # Show errors in interface
        quiet=False,            # Show startup information
        inbrowser=True,         # Auto-open browser
        favicon_path=None,      # Add custom favicon if desired
        auth=None              # Add authentication if needed: ("username", "password")
    )