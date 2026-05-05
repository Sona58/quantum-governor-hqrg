FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/home/q-worker/app/src"
ENV PATH="/home/q-worker/.local/bin:${PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user first
RUN adduser --disabled-password --gecos "" q-worker
WORKDIR /home/q-worker/app

# Switch to the user for the rest of the operations
USER q-worker

# Install dependencies as the q-worker user
COPY --chown=q-worker:q-worker requirements.txt .
RUN pip install --user --no-cache-dir nats-py grpcio protobuf numpy prometheus_client

# Copy source code
COPY --chown=q-worker:q-worker src/ ./src/

# Run the worker using the module flag
CMD ["python", "-m", "src.worker"]