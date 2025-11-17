import json
import re
from typing import List, Dict, Any
from .llm_client import chat as llm_chat, MissingAPIKeyError
from .models import ROIInput, ROIResult
from .roi_engine import run_model
from .pdf_generator import generate_report


SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are a Vinturas ROI assistant.\n"
        "Your job is to gather these fields from the conversation:\n"
        "company_name, industry, revenue (USD), cogs_pct (decimal),\n"
        "logistics_cost_pct (decimal), exception_cost_pct (decimal),\n"
        "avg_inventory_value (optional), logistics_planner_fte (optional).\n"
        "If revenue, logistics_cost_pct, or exception_cost_pct are missing or unclear,\n"
        "ask a short, clear follow-up question instead of guessing.\n"
        "When you have all required fields and the user has confirmed they are OK,\n"
        "output this exact pattern:\n\n"
        "ACTION:CALL_BACKEND\n"
        "{\n"
        "  \"company_name\": \"...\",\n"
        "  \"industry\": \"...\",\n"
        "  \"revenue\": ...,\n"
        "  \"cogs_pct\": ...,\n"
        "  \"logistics_cost_pct\": ...,\n"
        "  \"exception_cost_pct\": ...,\n"
        "  \"avg_inventory_value\": ...,\n"
        "  \"logistics_planner_fte\": ...\n"
        "}\n\n"
        "Otherwise, just continue the conversation normally."
    ),
}


def _extract_payload(text: str) -> Dict[str, Any]:
    m = re.search(r"ACTION:CALL_BACKEND\s*(\{[\s\S]*?\})", text)
    if not m:
        return {}
    block = m.group(1)
    try:
        data = json.loads(block)
        return data
    except Exception:
        return {}


def handle_roi_chat(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    try:
        model_text = llm_chat([SYSTEM_PROMPT] + messages)
    except MissingAPIKeyError as e:
        return {"reply": str(e), "metrics": None, "pdf_base64": None, "filename": None}
    except Exception as e:
        joined = "\n".join([m.get("content", "") for m in messages])
        payload = _extract_payload(joined)
        if not payload:
            return {"reply": str(e), "metrics": None, "pdf_base64": None, "filename": None}
        roi_input = ROIInput(**payload)
        result = run_model(roi_input)
        pdf = generate_report(roi_input, result)
        roi_pct = result["roi_percent"]
        payback = result["payback_months"]
        summary = (
            f"Calculated ROI is {roi_pct:.2f}%"
            + (f" with payback in {payback:.1f} months" if payback is not None else " with payback not applicable")
            + ". A PDF report is available."
        )
        metrics = ROIResult(
            inputs=result["inputs"],
            derived_metrics=result["derived_metrics"],
            savings_breakdown=result["savings_breakdown"],
            totals=result["totals"],
            roi_percent=result["roi_percent"],
            payback_months=result["payback_months"],
        )
        return {"reply": summary, "metrics": metrics, "pdf_base64": pdf["pdf_base64"], "filename": pdf["filename"]}

    payload = _extract_payload(model_text)
    if not payload:
        return {"reply": model_text, "metrics": None, "pdf_base64": None, "filename": None}

    roi_input = ROIInput(**payload)
    result = run_model(roi_input)
    pdf = generate_report(roi_input, result)
    roi_pct = result["roi_percent"]
    payback = result["payback_months"]
    summary = (
        f"Calculated ROI is {roi_pct:.2f}%"
        + (f" with payback in {payback:.1f} months" if payback is not None else " with payback not applicable")
        + ". A PDF report is available."
    )

    metrics = ROIResult(
        inputs=result["inputs"],
        derived_metrics=result["derived_metrics"],
        savings_breakdown=result["savings_breakdown"],
        totals=result["totals"],
        roi_percent=result["roi_percent"],
        payback_months=result["payback_months"],
    )

    return {
        "reply": summary,
        "metrics": metrics,
        "pdf_base64": pdf["pdf_base64"],
        "filename": pdf["filename"],
    }