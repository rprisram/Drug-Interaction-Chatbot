# Drug Interaction Chatbot: Fine-Tuning & GCP Deployment

This project implements a sophisticated Drug Interaction Chatbot using a Llama 3.1 8B model, specifically fine-tuned for this task, and deployed as a scalable, secure 3-tier architecture on Google Cloud Platform (GCP).

## ☁️ Cloud Architecture Overview

The application utilizes a decoupled, 3-tier architecture for robustness, security, and scalability:

1.  **Frontend (Gradio UI):**
    * A user-friendly interface built with Gradio.
    * Containerized using Docker.
    * Deployed as a public-facing, serverless service on **Google Cloud Run** (`ddi-frontend-service`). Handles user input and displays results. It sends requests to the API Gateway.

2.  **API Gateway:**
    * Provides a secure, public HTTPS endpoint (`ddi-gateway`) for the application.
    * Routes incoming requests from the Gradio frontend to the private Cloud Run backend service.
    * Authenticates itself to the backend using a dedicated **Service Account** (`api-gateway-invoker@...`) and **IAM Invoker roles**, ensuring the backend remains protected.

3.  **Application Backend (FastAPI):**
    * A FastAPI application acting as the central logic hub.
    * Containerized using Docker.
    * Deployed as a **private** serverless service on **Google Cloud Run** (`ddi-backend-service`) configured with `--no-allow-unauthenticated`.
    * Receives authenticated requests *only* from the API Gateway.
    * Formats prompts (including history) and securely calls the Vertex AI model endpoint using its own service identity.

4.  **Model Serving (Vertex AI Endpoint):**
    * Serves the **fine-tuned Llama 3.1 8B Q8_0 GGUF model** (details below).
    * Uses a custom container (**FastAPI + `llama-cpp-python`**) deployed to a **Vertex AI Endpoint** (`ddi-endpoint`).
    * Leverages **GPU acceleration** (e.g., NVIDIA T4) for fast inference.
    * The container automatically downloads the specified GGUF model file from **Google Cloud Storage (GCS)** upon startup, using necessary GCS permissions granted to its internal service account.

---

## 🔬 Model Fine-Tuning Process

The core of the chatbot is an LLM specifically adapted for Drug-Drug Interaction (DDI) detection.

### Data Preparation and Preprocessing

* **Data Sourcing:** The foundational dataset for DDI was sourced from the **PyTDC** library (DrugBank subset).
* **Data Transformation:**
    * Numerical target classes were mapped to descriptive drug impact labels.
    * Drug synonyms were applied to enrich the dataset.
    * The original pipe-delimited data was **augmented** into a conversational format (`user` -> `assistant`) using specific chat templates, crucial for optimal LLM training.

### Fine-Tuning Methodology

* **Base Model:** Llama 3.1 8B Instruct (specifically an optimized version compatible with Unsloth).
* **Efficient Fine-Tuning:** Powered by **Unsloth** for optimized memory usage and training speed.
* **PEFT (LoRA):** Parameter-Efficient Fine-Tuning with Low-Rank Adaptation significantly reduced computational requirements.
* **Hardware:** Trained on a rented **NVIDIA RTX 4090 GPU**, meticulously monitoring VRAM and disk usage.
* **Quantization:** The base model was quantized prior to PEFT, further optimizing resource utilization.

### Evaluation

* An "LLM as a Judge" approach was used, comparing the fine-tuned model against the base model on a blind test set.
* The fine-tuned model achieved a score of **8.245** vs. the base model's **1.91**, representing a **331.68% performance increase**, validating the effectiveness of the specialized fine-tuning.
* *(Evaluation results and scripts can be found in the `/fine-tuning/evaluation` directory - if applicable)*.

### Model Artifact

* The final fine-tuned model was saved in the **Q8_0 GGUF** format for efficient inference.
* This GGUF file is hosted on **Google Cloud Storage** and is downloaded by the Vertex AI serving container (Tier 4) during startup. *(The model file itself is not included in this repository due to its size)*.

*(Fine-tuning notebook/scripts can be found in the `/fine-tuning` directory - if applicable)*.

---

## 🚀 Accessing the Deployed Application

The chatbot is accessible via the public URL provided by the **Cloud Run** service hosting the Gradio frontend (`ddi-frontend-service`).

Currently, Model is undeployed to save the incurred costs, for demo, redeploy the model from the endpoint from vertex AI endpoints for v6 version of the model.

*(My DDI App URL structure)*

`https://ddi-frontend-service-1060363419011.us-central1.run.app/`

---

## ✨ Features

### 🎯 Core Functionality
- **Specialized Drug Interaction Analysis** using the **fine-tuned LLM** with structured responses.
- **Scalable Cloud Deployment** leveraging GCP serverless (Cloud Run, API Gateway) and AI infrastructure (Vertex AI).
- **Secure 3-Tier Architecture** with a private backend protected by API Gateway and IAM.

### 🔧 Technical Features
- **Optimized Prompt Engineering** including conversation history management in the backend.
- **GPU-Accelerated Inference** via Vertex AI Endpoints serving the custom GGUF model.
- **Containerized Services** (Docker) deployed on Cloud Run and Vertex AI.
- **Automated Model Download** from GCS within the serving container.
- **Serverless Scaling** (including scale-to-zero) via Cloud Run for frontend/backend.
- **Managed Authentication** between services via API Gateway and IAM.

### 🎨 User Experience
- **Medical Disclaimer** prominently displayed.
- **Example Questions** to guide users.
- **Quick Reference Guide** for effective usage.
- **Professional Styling** appropriate for medical context.

---

## 💻 Local Backend Execution (for Development/Testing)

You can run the FastAPI application backend locally to test its logic. This setup connects to your **deployed Vertex AI Endpoint** on Google Cloud.

### Prerequisites

1.  **Clone the Repository:** Ensure you have the project code locally.
2.  **Install Backend Dependencies:** Navigate to the `app-backend/` directory and install the required packages.
    ```bash
    cd app-backend
    pip install -r requirements.txt
    ```
3.  **Google Cloud Authentication (Local):** Authenticate your local environment to allow the backend to call GCP services. Run this command once in your terminal and follow the browser login prompts:
    ```bash
    gcloud auth application-default login
    ```
4.  **Backend Environment Variables:** Ensure the necessary environment variables are set for your terminal session. You can do this by creating a `.env` file in the `app-backend/` directory (requires `python-dotenv` installed, see `main.py`) or by exporting them directly:
    * **Using `.env` file (`app-backend/.env`):**
        ```dotenv
        GCP_PROJECT_ID=drug-to-drug-interaction
        GCP_REGION=us-central1
        VERTEX_ENDPOINT_ID=[YOUR_DEPLOYED_VERTEX_AI_ENDPOINT_ID] # The numeric ID
        ```
    * **Using `export` (run in the terminal before starting Uvicorn):**
        ```bash
        export GCP_PROJECT_ID="drug-to-drug-interaction"
        export GCP_REGION="us-central1"
        export VERTEX_ENDPOINT_ID="[YOUR_DEPLOYED_VERTEX_AI_ENDPOINT_ID]"
        ```

### Running the Server

1.  **Navigate to the `app-backend/` directory** in your terminal (if not already there).
2.  **Start the Uvicorn server:**
    ```bash
    uvicorn main:app --reload --port 8000
    ```
3.  The backend API will now be running locally, typically at `http://127.0.0.1:8000`. You can test it using tools like `curl` or Postman, sending requests to `http://127.0.0.1:8000/chat` (POST) or `http://127.0.0.1:8000/health` (GET). Remember that it will make live calls to your Vertex AI endpoint.

---

## 🛠️ Deployment Notes (For Maintainers)

* **Source Code:** Organized into three primary directories: `gradio-ui`, `app-backend`, `model-api`. *(Optionally add fine-tuning and evaluation directories)*.
* **Deployment:** Uses `gcloud` CLI commands to build containers (`gcloud builds submit`), manage artifacts (`Artifact Registry`, `GCS`), deploy services (`gcloud run deploy`), configure API Gateway (`gcloud api-gateway ...`), and manage the Vertex AI Endpoint (`gcloud ai models upload`, `gcloud ai endpoints deploy-model`).
* **Authentication:**
    * Frontend to Backend: Public Gradio calls the public API Gateway. The Gateway uses its dedicated service account (`api-gateway-invoker@...`) with the `roles/run.invoker` permission on the backend service to authenticate its requests.
    * Backend to Vertex AI: The backend Cloud Run service uses its assigned service account (with necessary Vertex AI permissions) to call the Vertex AI endpoint.
    * Model Container to GCS: The Vertex AI endpoint's internal service account (`custom-online-prediction@...`) needs `roles/storage.objectViewer` on the GCS bucket/object containing the model.
* **Environment Variables:** Key configurations like the API Gateway URL (for the frontend), GCS model path (for the model container), and Vertex AI endpoint ID (for the backend) are passed via environment variables during deployment (`--set-env-vars` for Cloud Run, `--container-env-vars` for Vertex AI model upload).
* **Cost:** Be mindful of Vertex AI Endpoint costs (GPU/machine uptime) and potentially API Gateway costs (request-based). Cloud Run costs are primarily request-based. Consider setting Vertex AI `min-replica-count=0` or undeploying the model when not in use to manage costs.

This GCP-deployed implementation provides a robust, scalable, and secure platform for the specialized drug interaction chatbot, leveraging multiple managed services for an efficient MLOps workflow from fine-tuning to production serving.