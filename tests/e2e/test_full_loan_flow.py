# -*- coding: utf-8 -*-

import requests
import time
import redis

def test_full_system_flow():
    # 1. Send request to Gateway
    payload = {"user_id": "portfolio-test", "loan_amount": 2000000}
    response = requests.post("http://localhost/analyze-risk", json=payload)
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # 2. Wait for the asynchronous pipeline to finish (NATS -> Executor -> Analyzer)
    time.sleep(5) 

    # 3. Verify Redis was updated by the Cost Analyzer
    r = redis.Redis(host='localhost', port=6379, db=0)
    audit_log = r.get(f"audit:{job_id}")
    
    assert audit_log is not None
    print(f"✅ Full flow verified for Job {job_id}")