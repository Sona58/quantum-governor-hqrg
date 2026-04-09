# -*- coding: utf-8 -*-

from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
CIRCUIT_EXECUTIONS = Counter(
    'quantum_circuit_executions_total', 
    'Total number of quantum circuits run',
    ['subject', 'engine']
)

INFERENCE_LATENCY = Histogram(
    'quantum_inference_duration_seconds',
    'Time spent performing quantum inference',
    ['engine']
)

def start_metrics_server(port=8000):
    """Starts the Prometheus metrics endpoint."""
    start_http_server(port)