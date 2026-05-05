# -*- coding: utf-8 -*-

import pytest
from services.gateway_api.src.logic import get_target_subject

def test_high_value_loan_tiering():
    # Loans > $1M should go to high_priority QPU
    subject = get_target_subject(amount=1500000, tier="enterprise")
    assert subject == "quantum.qpu.high_priority"

def test_standard_loan_tiering():
    # Small loans should stay on simulators
    subject = get_target_subject(amount=50000, tier="standard")
    assert subject == "quantum.simulator.standard"