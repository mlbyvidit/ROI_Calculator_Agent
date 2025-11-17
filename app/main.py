from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from .models import ROIInput, ROIResult, ReportResponse
from .roi_engine import run_model
from .pdf_generator import generate_report
from .agent import handle_roi_chat


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    reply: str
    metrics: Optional[ROIResult] = None
    pdf_base64: Optional[str] = None
    filename: Optional[str] = None


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


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(body: ChatRequest):
    msgs = [{"role": m.role, "content": m.content} for m in body.messages]
    r = handle_roi_chat(msgs)
    return ChatResponse(
        reply=r["reply"],
        metrics=r.get("metrics"),
        pdf_base64=r.get("pdf_base64"),
        filename=r.get("filename"),
    )


@app.get("/")
def root():
    return FileResponse("static/index.html")