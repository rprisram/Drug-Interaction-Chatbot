# ---- runtime ----
# We only need the runtime image now. No more builder.
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    python3-venv \
    libgomp1 && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY requirements.txt /app/requirements.txt

# [cite_start]Install basic requirements from your file [cite: 3]
RUN pip install --no-cache-dir -r requirements.txt
# Install numpy
RUN pip install --no-cache-dir numpy==2.2.6

# --- THIS IS THE FIX ---
# [cite_start]Install the specific llama-cpp-python version [cite: 1] with the 
# pre-built CUDA 12.2 wheel. This skips all compilation.
RUN pip install --no-cache-dir llama-cpp-python==0.3.16 --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu122
# --- END FIX ---

COPY . .
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]