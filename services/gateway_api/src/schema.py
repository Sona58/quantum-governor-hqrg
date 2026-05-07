# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field, BeforeValidator
from typing import Dict, Any, Optional, Annotated

CaseInsensitiveStr = Annotated[
    str, 
    BeforeValidator(lambda v: v.upper() if isinstance(v, str) else v)
]

class RiskAnalysisRequest(BaseModel):
    user_id: str
    user_tier: CaseInsensitiveStr = Field(..., pattern="^(FREE|PRO|ENTERPRISE)$")
    loan_amount: float
    # Parameters for the QML model (e.g., feature vectors)
    data_payload: Dict[str, Any] 
    
class AnalysisResponse(BaseModel):
    request_id: str
    status: str
    assigned_route: str
    estimated_wait: Optional[float] = None