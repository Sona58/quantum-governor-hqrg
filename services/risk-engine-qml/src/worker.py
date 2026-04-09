import asyncio
import json
import time
import nats
import numpy as np
from prometheus_client import start_http_server
from .models.qnn_risk import QuantumRiskScorer
from .utils.data_preprocessor import normalize_features
from .utils.circuit_logger import log_circuit_complexity
from .utils.metrics_exporter import start_metrics_server, CIRCUIT_EXECUTIONS, INFERENCE_LATENCY

class RiskWorker:
    def __init__(self, nats_url: str, subjects: list, engine_name: str):
        self.nats_url = nats_url
        self.subjects = subjects
        self.engine_name = engine_name
        self.scorer = QuantumRiskScorer()

    async def run(self):
        # Start Prometheus exporter on port 8001 (standard for K8s sidecars)
        start_metrics_server(8001)
        
        nc = await nats.connect(self.nats_url)
        print(f"Worker [{self.engine_name}] connected to NATS")

        async def message_handler(msg):
            start_time = time.perf_counter()
            data = json.loads(msg.data.decode())
            request_id = data.get("request_id")
            raw_features = data.get("data", {}).get("features", [])

            # 1. Pre-process (Classical Bridge)
            processed_data = normalize_features(raw_features)

            # 2. Audit the complexity before running
            # Access the internal circuit from our scorer
            log_circuit_complexity(self.scorer.qnn.circuit, request_id)

            # 3. Quantum Inference with Latency tracking
            with INFERENCE_LATENCY.labels(engine=self.engine_name).time():
                risk_score = self.scorer.predict(processed_data)

            # 4. Update Execution Counter
            CIRCUIT_EXECUTIONS.labels(subject=msg.subject, engine=self.engine_name).inc()

            # 5. Return Results
            result_payload = {
                "request_id": request_id,
                "risk_score": round(risk_score, 4),
                "metrics": {
                    "latency": time.perf_counter() - start_time,
                    "engine": self.engine_name
                }
            }
            await nc.publish(f"results.{request_id}", json.dumps(result_payload).encode())

        for subject in self.subjects:
            await nc.subscribe(subject, cb=message_handler)

        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    # These would be injected via K8s deployment env vars
    import os
    NATS_URL = os.getenv("NATS_URL", "nats://nats-service:4222")
    ENGINE_TYPE = os.getenv("ENGINE_TYPE", "qiskit-aer-sim") # e.g., 'ibm-qpu' for enterprise pods
    
    # Start Prometheus metrics server on port 8000
    # This allows the Prometheus pod to scrape this worker
    start_http_server(8000)
    
    worker = RiskWorker(NATS_URL, ["quantum.simulator.*"], ENGINE_TYPE)
    asyncio.run(worker.run())