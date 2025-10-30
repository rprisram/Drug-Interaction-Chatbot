from fastapi import FastAPI
from pydantic import BaseModel
import os
from llama_cpp import Llama
from typing import List
from google.cloud import storage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Instance(BaseModel):
    prompt: str

class PredictionPayload(BaseModel):
    instances: List[Instance]

app = FastAPI()
llm = None

def download_model_from_gcs():
    gcs_model_path = os.environ.get("GCS_MODEL_PATH") # e.g., "gs://llama3-ft-ddi-q8/unsloth.Q8_0.gguf"
    local_model_dir = "/app/model_files/" # Directory inside the container to save the model
    
    if not gcs_model_path:
        raise ValueError("GCS_MODEL_PATH environment variable not set.")
        
    os.makedirs(local_model_dir, exist_ok=True) # Create the local directory if it doesn't exist
    
    # Parse GCS path
    if not gcs_model_path.startswith("gs://"):
        raise ValueError(f"Invalid GCS path: {gcs_model_path}")
        
    path_parts = gcs_model_path[5:].split("/", 1)
    bucket_name = path_parts[0]
    blob_name = path_parts[1]
    local_filename = os.path.basename(blob_name)
    local_model_path = os.path.join(local_model_dir, local_filename)

    logger.info(f"Checking if model exists locally at {local_model_path}")
    # Only download if the file doesn't already exist locally
    if not os.path.exists(local_model_path):
        logger.info(f"Model not found locally. Downloading from gs://{bucket_name}/{blob_name}...")
        try:
            storage_client = storage.Client()
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            blob.download_to_filename(local_model_path)
            logger.info(f"Model downloaded successfully to {local_model_path}")
        except Exception as e:
            logger.error(f"Failed to download model from GCS: {e}")
            raise # Re-raise the exception to prevent startup if download fails
    else:
        logger.info("Model already exists locally. Skipping download.")
        
    return local_model_path

'''def get_env():
    print("--- All Environment Variables ---")
    for key, value in os.environ.items():
        print(f"{key}={value}")
    print("---------------------------------")
    app_dir = "/app"
    print(f"--- Contents of '{app_dir}' ---")
    try:
        print(os.listdir(app_dir))
    except Exception as e:
        print(f"Could not list contents of {app_dir}: {e}")
    print("---------------------------------")
    #AIP_STORAGE_URI: The cloud path where your model comes from.: gs://llama3-ft-ddi-q8/unsloth.Q8_0.gguf
    #https://storage.cloud.google.com/llama3-ft-ddi-q8/unsloth.Q8_0.gguf

    #AIP_MODEL_DIR: The local path inside the container where your model has been downloaded to.
    model_directory = os.environ.get('AIP_MODEL_DIR')
    print(f"Value of AIP_MODEL_DIR: {model_directory}")

    if model_directory:
        # 3. List the contents of that directory
        print(f"Contents of '{model_directory}':")
        try:
            # This will show you exactly what files Vertex AI downloaded
            print(os.listdir(model_directory))
        except Exception as e:
            print(f"Could not list directory contents: {e}")
    else:
        print("AIP_MODEL_DIR is not set. Cannot proceed to find model file.")

def resolve_model_path():
    get_env()
    model_directory = os.environ.get('AIP_MODEL_DIR') or os.environ.get('MODEL_DIR') or 'app/models/'
    model_filename = "unsloth.Q8_0.gguf" 
    # 3. Join the directory and filename to get the full path
    model_path = os.path.join(model_directory, model_filename)
    if not os.path.exists(model_path):
        # Optional: try to auto-discover a .gguf file
        for f in os.listdir(model_directory):
            if f.endswith(".gguf"):
                return os.path.join(model_directory, f)
        raise FileNotFoundError(f"Model file not found at: {model_path}")
    return model_path 

def get_llm():
    global llm
    if llm is None:
        model_path = resolve_model_path()
        llm = Llama(model_path=model_path, n_gpu_layers=35, verbose =True, n_ctx=4096)
    return llm '''

# --- Function to initialize the LLM (called on demand) ---
def get_llm():
    global llm
    if llm is None:
        try:
            local_model_path = download_model_from_gcs()
            logger.info(f"Loading model from {local_model_path}...")
            # Adjust n_gpu_layers as needed for your GPU. -1 tries to offload all.
            llm = Llama(model_path=local_model_path, n_gpu_layers=-1, verbose=True, n_ctx=4096) 
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            # Optionally handle this more gracefully, but raising often helps debug startup issues
            raise RuntimeError(f"Failed to initialize LLM: {e}") 
    return llm

@app.get('/health')
def health_check():
    return {'status': 'ok'}

@app.post('/predict')
def predict(payload: PredictionPayload):
    try:
        if not payload.instances:
            logger.warning("Received predict request with no instances.")
            return {"error": "No Instances block found"}
        request_prompt = payload.instances[0].prompt
        engine = get_llm()
        output = engine(request_prompt, max_tokens= 1500, echo=False, stop=['<|eot_id|>','<|end_of_text|>'])
        logger.info("Prediction generated successfully.")
        return {'predictions': [output['choices'][0]['text']]}
    except Exception as e:
        logger.error(f"Error during prediction: {e}", exc_info=True)
        return {'error': str(e)}