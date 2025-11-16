from typing import Dict, Any
from .models import ROIInput
from .config import get_benchmarks


def _round(v: float) -> float:
    return float(round(v, 2))


def run_model(inp: ROIInput) -> Dict[str, Any]:
    b = get_benchmarks(inp.industry)
    revenue = float(inp.revenue)
    cogs = revenue * float(inp.cogs_pct)
    logistics_cost = revenue * float(inp.logistics_cost_pct)
    exception_cost = revenue * float(inp.exception_cost_pct)
    gross_margin = revenue - cogs
    inventory_turns_bm = float(b["inventory_turns_benchmark"]) if b.get("inventory_turns_benchmark") else 8.0
    avg_inventory_value = inp.avg_inventory_value if inp.avg_inventory_value is not None else (cogs / inventory_turns_bm)
    fte_input = inp.logistics_planner_fte if inp.logistics_planner_fte is not None else max(1.0, (revenue / 100_000_000.0) * float(b["planner_fte_per_100m_revenue"]))

    derived = {
        "revenue": _round(revenue),
        "cogs": _round(cogs),
        "gross_margin": _round(gross_margin),
        "logistics_cost": _round(logistics_cost),
        "exception_cost": _round(exception_cost),
        "avg_inventory_value": _round(float(avg_inventory_value)),
        "logistics_planner_fte": float(fte_input),
    }

    exc_red = exception_cost * float(b["exception_reduction_pct"])
    log_opt = logistics_cost * float(b["logistics_optimization_pct"])
    inv_reduction_value = float(avg_inventory_value) * float(b["inventory_reduction_pct"])
    carrying_rate = float(b["carrying_cost_rate"])
    carrying_savings = inv_reduction_value * carrying_rate
    one_time_cash_release = inv_reduction_value
    planner_impr = float(b["planner_productivity_improvement_pct"]) 
    planner_cost = float(b["planner_fully_loaded_cost"]) 
    planner_cost_avoidance = float(fte_input) * planner_impr * planner_cost

    recurring_ebit_savings = exc_red + log_opt + carrying_savings
    cost_avoidance = planner_cost_avoidance
    annual_platform_cost = float(b["annual_platform_cost"]) 
    implementation_cost = float(b["implementation_cost"]) 
    total_annual_benefit = recurring_ebit_savings + cost_avoidance
    total_one_time_benefit = one_time_cash_release
    net_first_year_benefit = total_annual_benefit + total_one_time_benefit - annual_platform_cost - implementation_cost
    investment = annual_platform_cost + implementation_cost
    roi_percent = 0.0 if investment == 0 else (net_first_year_benefit / investment) * 100.0

    monthly_net_run_rate = (total_annual_benefit - annual_platform_cost) / 12.0
    payback_numerator = implementation_cost - total_one_time_benefit
    payback_months = None
    if monthly_net_run_rate > 0:
        payback_months = payback_numerator / monthly_net_run_rate if payback_numerator > 0 else 0.0

    savings_breakdown = {
        "exception_reduction": _round(exc_red),
        "logistics_optimization": _round(log_opt),
        "inventory_carrying_savings": _round(carrying_savings),
        "one_time_cash_release": _round(one_time_cash_release),
        "planner_cost_avoidance": _round(planner_cost_avoidance),
    }

    totals = {
        "recurring_ebit_savings": _round(recurring_ebit_savings),
        "cost_avoidance": _round(cost_avoidance),
        "annual_platform_cost": _round(annual_platform_cost),
        "implementation_cost": _round(implementation_cost),
        "total_annual_benefit": _round(total_annual_benefit),
        "total_one_time_benefit": _round(total_one_time_benefit),
        "net_first_year_benefit": _round(net_first_year_benefit),
    }

    result = {
        "inputs": inp.model_dump(),
        "derived_metrics": derived,
        "savings_breakdown": savings_breakdown,
        "totals": totals,
        "roi_percent": _round(roi_percent),
        "payback_months": None if payback_months is None else _round(payback_months),
    }
    return result