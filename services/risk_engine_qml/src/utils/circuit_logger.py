# -*- coding: utf-8 -*-

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QuantumLogger")

def log_circuit_complexity(circuit, request_id: str):
    """
    Analyzes the Qiskit circuit and logs its depth and gate count.
    This helps in auditing why a certain 'Quantum Cost' was incurred.
    """
    ops = circuit.count_ops()
    depth = circuit.depth()
    
    logger.info(f"--- Circuit Audit [{request_id}] ---")
    logger.info(f"Depth: {depth}")
    logger.info(f"Gate Count: {dict(ops)}")
    
    return {"depth": depth, "ops": dict(ops)}