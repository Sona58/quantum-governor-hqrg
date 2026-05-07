# -*- coding: utf-8 -*-

from services.gateway_api.src.governer import ResourceGovernor

def test_high_value_loan_tiering():
    resource_governer = ResourceGovernor()
    # Loans > $1M should go to high_priority QPU
    subject = resource_governer.determine_route(loan_amount=1500000.0, user_tier="enterprise")
    assert subject == "quantum.qpu.high_priority"

def test_standard_loan_tiering():
    resource_governer = ResourceGovernor()
    # Small loans should stay on simulators
    subject = resource_governer.determine_route(loan_amount=50000, user_tier="standard")
    assert subject == "quantum.simulator.standard"
    
def test_precision_loan_tiering():
    resource_governer = ResourceGovernor()
    # Medium loans should stay on simulators but with precision
    subject = resource_governer.determine_route(loan_amount=150000, user_tier="pro")
    assert subject == "quantum.simulator.precision"