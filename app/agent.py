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
        "You are the Vinturas ROI Assistant.\n"
        "Your goal is to interact naturally, gather business inputs, and help users\n"
        "calculate their Return on Investment using the backend ROI API.\n\n"

        "You MUST collect the following fields:\n"
        " - company_name (string)\n"
        " - industry (string)\n"
        " - revenue (number, USD)\n"
        " - cogs_pct (decimal, e.g., 0.53)\n"
        " - logistics_cost_pct (decimal)\n"
        " - exception_cost_pct (decimal)\n"
        "Optional:\n"
        " - avg_inventory_value (number)\n"
        " - logistics_planner_fte (number)\n\n"

        "RULES FOR THE CONVERSATION:\n"
        "1. Ask **only one follow-up question at a time**.\n"
        "2. NEVER repeat previously provided values.\n"
        "3. NEVER assume missing values — always ask.\n"
        "4. Keep questions short and easy to answer.\n"
        "5. When all required fields are collected, say:\n"
        "   'Great — I have all the info. Should I calculate the ROI now?'\n"
        "   and WAIT for explicit confirmation like 'yes' or 'calculate it'.\n\n"

        "WHEN USER CONFIRMS CALCULATION:\n"
        "Output ONLY this exact format:\n"
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

        "IMPORTANT:\n"
        "- Do NOT add comments, explanation, or text outside the JSON when sending ACTION:CALL_BACKEND.\n"
        "- If information is missing, continue the conversation normally.\n"
        "- If user asks unrelated questions, politely redirect.\n"
    )
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