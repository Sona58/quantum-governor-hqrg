# -*- coding: utf-8 -*-

class ResourceGovernor:
    @staticmethod
    def determine_route(loan_amount: float, user_tier: str) -> str:
        """
        Logic to maximize Business Yield vs. Quantum Cost.
        """
        # Tier 1: High-Value Enterprise (Direct to IBM QPU)
        if loan_amount >= 1_000_000 and user_tier == "ENTERPRISE":
            return "quantum.qpu.high_priority"
        
        # Tier 2: Mid-range or Pro users (High-precision Simulators)
        if loan_amount >= 100_000 or user_tier == "PRO":
            return "quantum.simulator.precision"
            
        # Tier 3: Standard (Local Standard Simulators)
        return "quantum.simulator.standard"