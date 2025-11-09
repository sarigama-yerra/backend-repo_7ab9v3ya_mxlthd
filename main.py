import os
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from database import db, create_document
from schemas import RafaelSession

app = FastAPI(title="RAFAEL — Medical Assistant for Clinicians")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "RAFAEL backend running"}

@app.post("/analyze")
async def analyze(
    role: str = Form(...),
    simple_view: str = Form("false"),
    symptoms: Optional[str] = Form(None),
    vitals: Optional[str] = Form(None),
    history: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None),
):
    """
    Simulated multi-model pipeline.
    In a real deployment, route text to Gemma-3 and media to Med-Gemma.
    Output is a strict JSON object consumable by the frontend.
    """

    # Parse boolean for simple_view
    simple_flag = str(simple_view).lower() in ("1", "true", "yes")

    # For this sandbox we don't call external models. We simulate outputs.
    text_reasoning = {
        "differential": [
            "Viral upper respiratory infection",
            "Bacterial pneumonia",
            "Asthma exacerbation",
        ],
        "rationale": "Symptoms and vitals suggest possible lower respiratory tract involvement.",
    }

    image_findings = {
        "imaging_modality": "unknown" if not image and not video else ("video" if video else "image"),
        "key_findings": [
            "No obvious fracture",
            "Possible left lower lobe opacity",
        ],
        "quality": "adequate",
    }

    summary = "Acute cough and dyspnea with possible infectious etiology; correlate imaging and vitals."

    integrated_assessment = (
        "Clinical features combined with imaging suggest community-acquired pneumonia; consider antibiotics if bacterial risk high."
    )

    next_steps = [
        "Order CBC, CMP, and CRP",
        "Obtain pulse oximetry monitoring",
        "Consider empiric antibiotics per local guidelines",
        "Reassess in 24-48 hours",
    ]

    patient_friendly = (
        "You likely have a chest infection. We'll check some blood tests and may start antibiotics. We'll keep an eye on your oxygen levels."
    )

    # Confidence score demo
    confidence = 0.78

    output = {
        "summary": summary,
        "text_reasoning": text_reasoning,
        "image_findings": image_findings,
        "integrated_assessment": integrated_assessment,
        "next_steps": next_steps,
        "patient_friendly": patient_friendly if simple_flag or role == "Patient" else "",
        "confidence": confidence,
    }

    # Persist session log
    try:
        doc = RafaelSession(
            role=role,
            simple_view=simple_flag,
            symptoms=symptoms,
            vitals=vitals,
            history=history,
            image_filename=image.filename if image else None,
            video_filename=video.filename if video else None,
            output=output,
            confidence=confidence,
        )
        create_document("rafaelsession", doc)
    except Exception:
        # If DB not available, continue without failing
        pass

    return JSONResponse(content=output)

@app.post("/export")
async def export_pdf(data: dict):
    """Return a simple PDF-like file (text-based) for sandbox demonstration."""
    # Note: avoiding external pdf libraries for minimal deps.
    text = ["RAFAEL — Clinical Report", "", "Sections:"]
    def add_section(title, value):
        text.append(f"\n== {title} ==")
        if isinstance(value, (dict, list)):
            import json
            text.append(json.dumps(value, indent=2))
        else:
            text.append(str(value))

    add_section("Summary", data.get("summary"))
    add_section("Text Reasoning", data.get("text_reasoning"))
    add_section("Image Findings", data.get("image_findings"))
    add_section("Integrated Assessment", data.get("integrated_assessment"))
    add_section("Recommended Next Steps", data.get("next_steps"))
    add_section("Patient-Friendly Summary", data.get("patient_friendly"))
    add_section("Confidence", data.get("confidence"))

    content = "\n".join(text)
    buf = BytesIO(content.encode("utf-8"))
    headers = {"Content-Disposition": "attachment; filename=rafael-report.pdf"}
    return StreamingResponse(buf, media_type="application/pdf", headers=headers)

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available" if db is None else "✅ Available",
    }
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
