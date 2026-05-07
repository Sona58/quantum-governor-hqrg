# -*- coding: utf-8 -*-

import requests
import time
import redis
import os

def test_full_system_flow():
    # Use env vars passed from CI/CD
    gateway_url = os.getenv("GATEWAY_URL", "http://localhost:8080")
    redis_host = os.getenv("REDIS_HOST", "localhost")

    # 1. Send request to Gateway (Notice the /analyze-risk append)
    payload = {
        "user_id": "user_789",
        "user_tier": "pro",
        "loan_amount": 75000,
        "complexity_threshold": 20,
        "data_payload": {
            "features": [0.1, 0.2, 0.3, 0.5]
        }
    }
    response = requests.post(f"{gateway_url}/analyze-risk", json=payload)
    
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # 2. Wait for async processing
    time.sleep(10) 

    # 3. Verify Redis
    r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    audit_log = r.get(f"audit:{job_id}")
    
    assert audit_log is not None
    print(f"✅ Full flow verified for Job {job_id}")