# -*- coding: utf-8 -*-

import uuid
import json
import grpc
import os
from fastapi import FastAPI, HTTPException
from prometheus_client import make_asgi_app, Counter

# Import existing schemas and the new SLURM provider
from schema import RiskAnalysisRequest, AnalysisResponse
from governer import ResourceGovernor
from utils.slurm_provider import MockSlurmProvider

# Import gRPC stubs
import risk_engine_pb2
import risk_engine_pb2_grpc
import nats

REQUEST_COUNT = Counter("gateway_requests_total", "Total requests handled by Gateway", ["route"])

app = FastAPI(title="HQRG Gateway API")
governor = ResourceGovernor()
slurm = MockSlurmProvider()

# Configuration
# risk-engine-service is K8s Service name defined in Terraform
RISK_ENGINE_GRPC_HOST = os.getenv("RISK_ENGINE_HOST", "risk-engine-service:50051")

# Add the prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.on_event("startup")
async def startup_event():
    # We will connect to NATS here
    app.state.nc = await nats.connect("nats://nats-service:4222")

@app.post("/analyze-risk", response_model=AnalysisResponse)
async def analyze_risk(request: RiskAnalysisRequest):
    # Increment the counter every time this is called
    route = "hpc" if len(request.data_payload.get("features", [])) > 20 else "grpc"
    REQUEST_COUNT.labels(route=route).inc()
    
    request_id = str(uuid.uuid4())
    
    # 1. Determine "Complexity" for Routing
    # Assume data_payload contains 'qubits'. If > 20, we offload to SLURM
    features = request.data_payload.get("features", [])
    qubit_count = len(features)
    
    # 2. HYBRID ROUTING LOGIC
    if qubit_count > 20:
        # PATH A: SLURM (HPC mode)
        slurm_result = slurm.submit_job(request.data_payload)
        return {
            "request_id": slurm_result["job_id"],
            "status": slurm_result["status"],
            "assigned_route": "hpc.slurm.queue"
        }
    
    else:
        # PATH B: K8s (Real-time gRPC Mode)
        try:
            # Create a synchronous gRPC channel
            with grpc.insecure_channel(RISK_ENGINE_GRPC_HOST) as channel:
                stub = risk_engine_pb2_grpc.RiskAnalysisStub(channel)
                
                # Call the Risk Engine directly
                response = stub.AnalyzeRisk(risk_engine_pb2.RiskRequest(
                    circuit_data = json.dumps(request.data_payload),
                    qubits = qubit_count,
                    depth = 10
                ))
                return {
                    "request_id": request_id,
                    "status": f"Success (Score: {response.risk_score})",
                    "assigned_route": "k8s.grpc.direct"
                }
    
        except grpc.RpcError as e:
            # If gRPC fails, return error
            print(f"gRPC failed: {e}")
            raise HTTPException(status_code=503, detail="Risk Engine unreachable via gRPC")
            