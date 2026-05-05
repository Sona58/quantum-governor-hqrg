# Use a slim Python 3.12 image for a smaller footprint
FROM python:3.12-slim

# Set environment variables to prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Create a non-privileged user to run the app (Security Best Practice)
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# NEW: Force APT to bypass caches and handle broken proxies
RUN echo 'Acquire::http::Pipeline-Depth 0;\n\
Acquire::http::No-Cache true;\n\
Acquire::BrokenProxy true;' > /etc/apt/apt.conf.d/99fixbadproxy

# Install system dependencies if needed (e.g., curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY src/ ./src/

# Switch to the non-privileged user
USER appuser

# Expose the port FastAPI runs on
EXPOSE 8000

# Start the application using uvicorn
# We use --host 0.0.0.0 to make it accessible within the K8s cluster
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]