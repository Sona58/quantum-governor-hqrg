import asyncio
import json
import time
import os
import nats
import grpc
from concurrent import futures
from prometheus_client import start_http_server

# Import the generated gRPC stubs
import risk_engine_pb2 as pb2
import risk_engine_pb2_grpc as pb2_grpc

from models.qnn_risk import QuantumRiskScorer
from utils.data_preprocessor import normalize_features
from utils.circuit_logger import log_circuit_complexity
from utils.metrics_exporter import start_metrics_server, CIRCUIT_EXECUTIONS, INFERENCE_LATENCY

# gRPC Servicer Implementation
class RiskEngineServicer(pb2_grpc.RiskAnalysisServicer):
    def __init__(self, worker_instance):
        self.worker = worker_instance

    def AnalyzeRisk(self, request, context):
        """gRPC Method: Direct Gateway-to-Engine communication"""
        try:
            # 1. Parse the JSON string back into a dictionary
            input_data = json.loads(request.circuit_data)
            raw_features = input_data.get("features", [])
            
            # 2. Process features
            processed_data = normalize_features(raw_features)
        
            # 3. Get Prediction
            with INFERENCE_LATENCY.labels(engine=self.worker.engine_name).time():
                risk_score = self.worker.scorer.predict(processed_data)
            
            CIRCUIT_EXECUTIONS.labels(subject="grpc.direct", engine=self.worker.engine_name).inc()
    
            return pb2.RiskResponse(
                risk_score=float(risk_score),
                provider_used=self.worker.engine_name
            )
        
        except Exception as e:
            context.set_details(f"Worker Error: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return pb2.RiskResponse()

class RiskWorker:
    def __init__(self, nats_url: str, subjects: list, engine_name: str):
        self.nats_url = nats_url
        self.subjects = subjects
        self.engine_name = engine_name
        self.scorer = QuantumRiskScorer()

    async def run_nats(self):
        """Handles existing NATS-based asynchronous jobs"""
        nc = await nats.connect(self.nats_url)
        print(f"Worker [{self.engine_name}] NATS connected")

        async def message_handler(msg):
            data = json.loads(msg.data.decode())
            raw_features = data.get("data", {}).get("features", [])
            
            processed_data = normalize_features(raw_features)
            risk_score = self.scorer.predict(processed_data)
            
            result_payload = {"risk_score": round(risk_score, 4), "engine": self.engine_name}
            await nc.publish(f"results.{data.get('request_id')}", json.dumps(result_payload).encode())

        for subject in self.subjects:
            await nc.subscribe(subject, cb=message_handler)

    def run_grpc(self):
        """Starts the gRPC Server for high-speed routing"""
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        pb2_grpc.add_RiskAnalysisServicer_to_server(RiskEngineServicer(self), server)
        server.add_insecure_port('[::]:50051')
        print(f"Worker [{self.engine_name}] gRPC Server starting on port 50051")
        server.start()
        server.wait_for_termination()

async def main():
    NATS_URL = os.getenv("NATS_URL", "nats://nats-service:4222")
    ENGINE_TYPE = os.getenv("ENGINE_TYPE", "qiskit-aer-sim")
    
    # 1. Start Prometheus metrics
    start_metrics_server(8000)
    
    worker = RiskWorker(NATS_URL, ["quantum.simulator.*"], ENGINE_TYPE)

    # 2. Run gRPC in a separate thread because it is blocking
    loop = asyncio.get_event_loop()
    grpc_task = loop.run_in_executor(None, worker.run_grpc)

    # 3. Run NATS in the main event loop
    await worker.run_nats()
    
    # Keep the main loop alive
    await asyncio.gather(grpc_task)

if __name__ == "__main__":
    asyncio.run(main())