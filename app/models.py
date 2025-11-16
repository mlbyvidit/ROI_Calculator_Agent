from pydantic import BaseModel
from typing import Optional, Dict, Any


class ROIInput(BaseModel):
    company_name: str
    industry: str
    revenue: float
    cogs_pct: float
    logistics_cost_pct: float
    exception_cost_pct: float
    avg_inventory_value: Optional[float] = None
    logistics_planner_fte: Optional[float] = None


class ROIResult(BaseModel):
    inputs: Dict[str, Any]
    derived_metrics: Dict[str, float]
    savings_breakdown: Dict[str, float]
    totals: Dict[str, float]
    roi_percent: float
    payback_months: Optional[float]


class ReportResponse(BaseModel):
    pdf_base64: str
    filename: str
    metrics: ROIResult