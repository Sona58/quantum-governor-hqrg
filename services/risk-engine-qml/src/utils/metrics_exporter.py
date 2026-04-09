# services/risk-engine-qml/src/utils/metrics_exporter.py
from prometheus_client import Counter, Histogram, Gauge

# Track how many jobs are processed by engine type (Simulator vs QPU)
JOBS_PROCESSED = Counter(
    'quantum_risk_jobs_total', 
    'Total number of risk analysis jobs',
    ['engine_type', 'status']
)

# Track actual time spent on the Quantum device
QPU_EXECUTION_TIME = Histogram(
    'quantum_qpu_duration_seconds',
    'Time spent executing circuits on IBM hardware',
    buckets=(1, 5, 10, 30, 60, 120, 300)
)

# Monitor the complexity of circuits being generated
CIRCUIT_DEPTH = Gauge(
    'quantum_circuit_depth',
    'Current depth of the generated QNN circuit',
    ['engine_type']
)