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
    
    # Debug print if validation fails
    if response.status_code != 200:
        print(f"❌ Detail: {response.json()}")
    
    assert response.status_code == 200

    data = response.json()
    # main.py returns "request_id", not "job_id"
    request_id = data["request_id"] 
    print(f"✅ Request accepted via route: {data['assigned_route']}")

    # 2. Wait for processing
    time.sleep(10) 

    # 3. Verify Redis
    # Note: Ensure your Risk Engine or Cost Analyzer actually writes to Redis 
    # using the 'request_id' as the key.
    r = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
    audit_log = r.get(f"audit:{request_id}")
    
    # If the gRPC path is synchronous, the audit log should exist immediately.
    assert audit_log is not None