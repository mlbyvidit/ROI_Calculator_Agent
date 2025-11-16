from fastapi import FastAPI
from .models import ROIInput, ROIResult, ReportResponse
from .roi_engine import run_model
from .pdf_generator import generate_report


app = FastAPI()


@app.post("/roi", response_model=ROIResult)
def roi(input_data: ROIInput):
    result = run_model(input_data)
    return ROIResult(
        inputs=result["inputs"],
        derived_metrics=result["derived_metrics"],
        savings_breakdown=result["savings_breakdown"],
        totals=result["totals"],
        roi_percent=result["roi_percent"],
        payback_months=result["payback_months"],
    )


@app.post("/roi/report", response_model=ReportResponse)
def roi_report(input_data: ROIInput):
    result = run_model(input_data)
    pdf = generate_report(input_data, result)
    return ReportResponse(pdf_base64=pdf["pdf_base64"], filename=pdf["filename"], metrics=ROIResult(
        inputs=result["inputs"],
        derived_metrics=result["derived_metrics"],
        savings_breakdown=result["savings_breakdown"],
        totals=result["totals"],
        roi_percent=result["roi_percent"],
        payback_months=result["payback_months"],
    ))