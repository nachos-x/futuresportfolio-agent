# Dockerfile for deploying the Energy Futures Monitor on GCP VM (or Cloud Run)
# Uses CPU-only PyTorch to keep image size reasonable (~1.5-2GB final)

FROM python:3.12-slim

# System dependencies (build tools sometimes needed by torch/scikit)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
# Use CPU torch explicitly to avoid pulling CUDA libs
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Streamlit configuration for container/VM use
# (can be overridden via .streamlit/config.toml or flags)
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Expose Streamlit port
EXPOSE 8501

# Default command — override with env for production tuning if needed
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
