# -*- coding: utf-8 -*-

import uuid
from fastapi import FastAPI, HTTPException
from .schemas import RiskAnalysisRequest, AnalysisResponse
from .governor import ResourceGovernor
import nats
import json

app = FastAPI(title="HQRG Gateway API")
governor = ResourceGovernor()

@app.on_event("startup")
async def startup_event():
    # We will connect to NATS here in the next step
    app.state.nc = await nats.connect("nats://nats-service:4222")

@app.post("/analyze-risk", response_model=AnalysisResponse)
async def analyze_risk(request: RiskAnalysisRequest):
    request_id = str(uuid.uuid4())
    
    # 1. Govern the request
    route = governor.determine_route(request.loan_amount, request.user_tier)
    
    # 2. Prepare payload for the NATS queue
    payload = {
        "request_id": request_id,
        "data": request.data_payload,
        "tier": request.user_tier
    }
    
    # 3. Publish to the determined subject
    await app.state.nc.publish(route, json.dumps(payload).encode())
    
    return {
        "request_id": request_id,
        "status": "Queued",
        "assigned_route": route
    }