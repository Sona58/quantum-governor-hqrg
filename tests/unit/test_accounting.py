# -*- coding: utf-8 -*-

from services.cost_analyzer.src.accounting import QuantumAccountant

def test_cost_multiplier_logic():
    quantum_accountant = QuantumAccountant()
    # Simulators should be cheap (e.g., 1.0 multiplier)
    sim_cost = quantum_accountant.calculate_cost(duration=10, engine="qiskit-aer-sim")
    # QPU should be expensive (e.g., 5.0 multiplier)
    qpu_cost = quantum_accountant.calculate_cost(duration=10, engine="ibm-qpu")
    
    assert qpu_cost > sim_cost