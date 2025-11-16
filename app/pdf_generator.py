import base64
from io import BytesIO
from typing import Dict, Any
from xhtml2pdf import pisa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .models import ROIInput


def _chart_base64(savings: Dict[str, float]) -> str:
    labels = ["Recurring", "One-time", "Avoidance"]
    values = [
        float(savings.get("recurring_ebit_savings", 0.0)),
        float(savings.get("total_one_time_benefit", 0.0)),
        float(savings.get("cost_avoidance", 0.0)),
    ]
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(labels, values, color=["#4caf50", "#2196f3", "#ff9800"]) 
    ax.set_ylabel("USD")
    ax.set_title("Savings Breakdown")
    for i, v in enumerate(values):
        ax.text(i, v, f"{int(v):,}", ha="center", va="bottom", fontsize=8)
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    b = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b


def _format_currency(v: float) -> str:
    return f"${v:,.0f}"


def generate_report(inp: ROIInput, result: Dict[str, Any]) -> Dict[str, Any]:
    dm = result["derived_metrics"]
    sb = result["savings_breakdown"]
    totals = result["totals"]
    chart_data = {
        "recurring_ebit_savings": totals.get("recurring_ebit_savings", 0.0),
        "total_one_time_benefit": totals.get("total_one_time_benefit", 0.0),
        "cost_avoidance": totals.get("cost_avoidance", 0.0),
    }
    chart_b64 = _chart_base64(chart_data)
    rows = [
        ("Revenue", _format_currency(dm["revenue"])) ,
        ("COGS", _format_currency(dm["cogs"])) ,
        ("Gross Margin", _format_currency(dm["gross_margin"])) ,
        ("Logistics Cost", _format_currency(dm["logistics_cost"])) ,
        ("Exception Cost", _format_currency(dm["exception_cost"])) ,
        ("Avg Inventory Value", _format_currency(dm["avg_inventory_value"])) ,
        ("Planner FTE", f"{dm['logistics_planner_fte']:.2f}") ,
    ]
    table_rows = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in rows])
    savings_rows = [
        ("Exception Reduction", _format_currency(sb["exception_reduction"])) ,
        ("Logistics Optimization", _format_currency(sb["logistics_optimization"])) ,
        ("Inventory Carrying Savings", _format_currency(sb["inventory_carrying_savings"])) ,
        ("Planner Cost Avoidance", _format_currency(sb["planner_cost_avoidance"])) ,
        ("One-time Cash Release", _format_currency(sb["one_time_cash_release"])) ,
    ]
    savings_table = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in savings_rows])
    summary = [
        ("Recurring EBIT Savings", _format_currency(totals["recurring_ebit_savings"])) ,
        ("Cost Avoidance", _format_currency(totals["cost_avoidance"])) ,
        ("Annual Platform Cost", _format_currency(totals["annual_platform_cost"])) ,
        ("Implementation Cost", _format_currency(totals["implementation_cost"])) ,
        ("One-time Benefit", _format_currency(totals["total_one_time_benefit"])) ,
        ("Net First-year Benefit", _format_currency(totals["net_first_year_benefit"])) ,
        ("ROI%", f"{result['roi_percent']:.2f}%") ,
        ("Payback Months", "N/A" if result["payback_months"] is None else f"{result['payback_months']:.1f}"),
    ]
    summary_table = "".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in summary])
    html = f"""
    <html>
    <head>
      <meta charset='utf-8'/>
      <style>
        body {{ font-family: Helvetica, Arial, sans-serif; }}
        h1 {{ color: #222; }}
        table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        .section {{ margin: 18px 0; }}
      </style>
    </head>
    <body>
      <h1>ROI Summary</h1>
      <div class='section'>
        <strong>Company</strong>: {inp.company_name}<br/>
        <strong>Industry</strong>: {inp.industry}
      </div>
      <div class='section'>
        <h2>Inputs & Derived Metrics</h2>
        <table><tbody>{table_rows}</tbody></table>
      </div>
      <div class='section'>
        <h2>Savings Breakdown</h2>
        <table><tbody>{savings_table}</tbody></table>
      </div>
      <div class='section'>
        <h2>Summary</h2>
        <table><tbody>{summary_table}</tbody></table>
      </div>
      <div class='section'>
        <h2>Chart</h2>
        <img src='data:image/png;base64,{chart_b64}' style='width:100%; max-width:600px;'/>
      </div>
    </body>
    </html>
    """
    pdf_buf = BytesIO()
    pisa.CreatePDF(html, dest=pdf_buf)
    pdf_b64 = base64.b64encode(pdf_buf.getvalue()).decode("utf-8")
    filename = f"ROI_{inp.company_name.replace(' ', '_')}.pdf"
    return {"pdf_base64": pdf_b64, "filename": filename}