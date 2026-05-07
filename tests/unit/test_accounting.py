# -*- coding: utf-8 -*-

from services.cost_analyzer.src.accounting import calculate_cost

def test_cost_multiplier_logic():
    # Simulators should be cheap (e.g., 1.0 multiplier)
    sim_cost = calculate_cost(duration=10, engine="qiskit-aer-sim")
    # QPU should be expensive (e.g., 5.0 multiplier)
    qpu_cost = calculate_cost(duration=10, engine="ibm-qpu")
    
    assert qpu_cost > sim_cost