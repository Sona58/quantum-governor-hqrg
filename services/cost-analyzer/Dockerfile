FROM python:3.12-slim

WORKDIR /app

# Upgrade pip first to handle SSL/TLS better and prevent the warning
RUN pip install --upgrade pip

COPY requirements.txt .

# Add --default-timeout to prevent connection drops from failing the build immediately
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    -r requirements.txt

COPY src/ ./src/

RUN adduser --disabled-password --gecos "" auditor
USER auditor

CMD ["python", "-m", "src.main"]