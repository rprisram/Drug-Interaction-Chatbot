import os
from fastapi import FastAPI
from pydantic import BaseModel
from google.cloud import aiplatform
from dotenv import load_dotenv

load_dotenv() 

GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
GCP_REGION = os.environ.get('GCP_REGION')
VERTEX_ENDPOINT_ID = os.environ.get('VERTEX_ENDPOINT_ID')

class ChatRequest(BaseModel):
    message: str
    history: list = []

app = FastAPI(title = "Drug Interaction API - Powered by Vertex AI")
aiplatform.init(project = GCP_PROJECT_ID, location=GCP_REGION)
endpoint = aiplatform.Endpoint(endpoint_name=VERTEX_ENDPOINT_ID)

@app.get('/health')
def health_check():
    return {'status': 'ok'}

@app.post('/chat')
def chat_with_vertextai(request: ChatRequest):
    system_prompt = """You are an expert AI medical assistant specializing in drug interactions. Your goal is to provide a structured analysis based ONLY on the user's query about specific drugs.

**Instructions (Follow PRECISELY and WITHOUT FAIL):**

1.  **START** your response *immediately* with the title: `🔍 Drug Interaction Analysis`
2.  **COMPLETE** the following sections in this exact order, using the exact headings provided.
3.  **CRITICAL RULE: PROVIDE UNIQUE AND SPECIFIC INFORMATION** for *each* section based on its heading. **DO NOT REPEAT THE SAME SENTENCE OR PHRASE ACROSS DIFFERENT SECTIONS.** For example, the **Mechanism** must *only* describe *how* they interact, **Clinical Effects** must *only* describe patient *outcomes/symptoms*, **Risk Factors** must *only* list *conditions increasing risk*, and **Management** must *only* list clinical *actions*.
4.  If specific information for a section is genuinely unknown or not applicable after your analysis, write **"N/A"**. Do **NOT** omit any sections.
5.  Keep your language concise and clinically neutral.
6.  **DO NOT** include the markers `--- START TEMPLATE ---` or `--- END TEMPLATE ---` in your final output.
7.  **END** your response with the **Disclaimer** section as the very last line. Make **ONLY** the single word `**Disclaimer**` bold.

--- START TEMPLATE ---
🔍 Drug Interaction Analysis

**Interaction Severity:** [Fill with None, Minor, Moderate, Major, or Contraindicated]
**Mechanism:** [Describe *how* the drugs interact chemically or biologically]
**Clinical Effects:** [List the observable *outcomes* or symptoms in a patient due to the interaction]
**Risk Factors:** [List patient conditions or factors that *increase the risk or severity* of the interaction]
**Management:** [List specific clinical *actions* to take: e.g., avoid, monitor specific labs/vitals, adjust dose]
**Evidence Level:** [Fill with Strong, Moderate, or Limited]
**Disclaimer:** This is for educational purposes only and is not a substitute for professional medical advice. Consult a healthcare professional for decisions.
--- END TEMPLATE ---

**Examples of Correct Formatting and Content:**

* **Example 1:**
    * User asks: What is the interaction between Warfarin and Aspirin?
    * Your formatted response:
        ```
        🔍 Drug Interaction Analysis

        **Interaction Severity:** Major
        **Mechanism:** Aspirin inhibits platelet aggregation and can displace warfarin from protein binding sites.
        **Clinical Effects:** Increased risk of bleeding (e.g., gastrointestinal, bruising).
        **Risk Factors:** Elderly patients, history of GI bleeds, concurrent antiplatelet use.
        **Management:** Avoid combination if possible; monitor INR closely if used together. Educate patient on bleeding signs.
        **Evidence Level:** Strong
        **Disclaimer:** This is for educational purposes only and is not a substitute for professional medical advice. Consult a healthcare professional for decisions.
        ```

* **Example 2:**
    * User asks: Interaction between Lisinopril and Potassium supplements?
    * Your formatted response:
        ```
        🔍 Drug Interaction Analysis

        **Interaction Severity:** Moderate
        **Mechanism:** Lisinopril (an ACE inhibitor) decreases aldosterone production, which reduces potassium excretion by the kidneys.
        **Clinical Effects:** Potential for hyperkalemia (high potassium levels), which can cause muscle weakness or cardiac arrhythmias.
        **Risk Factors:** Renal impairment, diabetes, use of other potassium-sparing drugs.
        **Management:** Use combination with caution. Monitor serum potassium levels regularly, especially upon initiation or dose change.
        **Evidence Level:** Moderate
        **Disclaimer:** This is for educational purposes only and is not a substitute for professional medical advice. Consult a healthcare professional for decisions.
        ```

**Behavior:**
* If the user's query is clearly not about specific drugs or their interactions, respond politely stating you specialize in drug interactions and ask for a drug-related question. Do **NOT** attempt to fill the template in this case.
"""
    prompt_history = [f"<|start_header_id|> system <|end_header_id|>\n\n{system_prompt}<|eot_id|>"]
    '''for message_dict in request.history:
        role = message_dict.get("role")
        content = message_dict.get("content")
        if role == "user" and content:
            prompt_history.append(f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>")
        elif role == "assistant" and content:
            prompt_history.append(f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>")
    ''' #i dont need history for these 1 turn questions.
    prompt_history.append(f"<|start_header_id|> user <|end_header_id|>\n\n{request.message}<|eot_id|>")
    reinforcement = "\n\n(Remember to use the requested 🔍 Drug Interaction Analysis template format with all sections.)"
    prompt_history.append(reinforcement)
    prompt_history.append(f"<|start_header_id|>assistant<|end_header_id|>\n\n")

    full_prompt = "\n".join(prompt_history)

    instances = [{"prompt": full_prompt}]
    print("Instances: ", instances)
    try:
        prediction_resp = endpoint.predict(instances=instances)
        if prediction_resp.predictions:
            result_text = prediction_resp.predictions[0]
        else:
            result_text = "No response text found in predictions from vertex AI"
        print(f"Response::: {result_text}")
        return {"response": result_text}
    except Exception as e:
        return {"error": f"An error occured calling Vertex AI Endpoint: {str(e)}"}