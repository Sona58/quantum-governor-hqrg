# -*- coding: utf-8 -*-

class QuantumAccountant:
    # Cost per execution in mock "Quantum Credits"
    PRICING_MODEL = {
        "qiskit-aer-sim": 0.01,        # Local simulation is cheap
        "qiskit-high-precision": 0.05, # Higher RAM/CPU usage
        "ibm-qpu": 5.00                # Real hardware is expensive
    }

    @classmethod
    def calculate_cost(cls, engine: str, duration: float) -> float:
        base_rate = cls.PRICING_MODEL.get(engine, 0.1)
        # We factor in duration to account for long-running complex circuits
        return round(base_rate + (duration * 0.01), 4)