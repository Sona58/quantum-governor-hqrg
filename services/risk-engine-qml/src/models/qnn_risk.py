# services/risk-engine-qml/src/qnn_risk.py
import time
from .utils.metrics_exporter import JOBS_PROCESSED, QPU_EXECUTION_TIME, CIRCUIT_DEPTH

def process_risk_analysis(circuit, engine_type):
    # 1. Record Circuit Complexity
    CIRCUIT_DEPTH.labels(engine_type=engine_type).set(circuit.depth())
    
    start_time = time.time()
    try:
        # 2. Execute Quantum Job
        result = execute_on_quantum(circuit, engine_type)
        
        # 3. If it was a real QPU, record the duration
        if engine_type == "ibm-qpu":
            duration = time.time() - start_time
            QPU_EXECUTION_TIME.observe(duration)
            
        JOBS_PROCESSED.labels(engine_type=engine_type, status="success").inc()
        return result
        
    except Exception as e:
        JOBS_PROCESSED.labels(engine_type=engine_type, status="error").inc()
        raise e