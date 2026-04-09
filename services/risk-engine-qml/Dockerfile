# Use a Python 3.12 image with build essentials
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into a virtual environment or local path
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Final Stage ---
FROM python:3.12-slim

WORKDIR /app

# Copy only the installed python packages from the builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Install libgomp (required for Qiskit Aer's high-performance simulation)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the source code (including models and utils)
COPY src/ ./src/

# Create a non-root user
RUN adduser --disabled-password --gecos "" q-worker
USER q-worker

# Run the worker
CMD ["python", "-m", "src.worker"]