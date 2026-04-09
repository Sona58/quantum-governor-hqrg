# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class RiskAnalysisRequest(BaseModel):
    user_id: str
    user_tier: str = Field(..., pattern="^(FREE|PRO|ENTERPRISE)$")
    loan_amount: float
    # Parameters for the QML model (e.g., feature vectors)
    data_payload: Dict[str, Any] 
    
class AnalysisResponse(BaseModel):
    request_id: str
    status: str
    assigned_route: str
    estimated_wait: Optional[float] = None