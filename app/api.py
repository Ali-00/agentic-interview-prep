from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from .models import UserInput, GenerateStudyGuideResponse
from .controller import controller_agent
from .config import settings
from .pdf_utils import html_to_pdf_bytes


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/generate-study-guide", response_model=GenerateStudyGuideResponse)
async def generate_study_guide(
    user_input: UserInput,
    include_pdf: bool = False,
):
    """
    Generate a structured, role-specific interview preparation study guide.

    Send JSON body matching `UserInput`. For file-based resumes/JDs, convert to
    text on the client side or use the multipart endpoint below.
    """
    resp = await controller_agent.generate_study_guide(
        user_input=user_input, include_pdf=include_pdf
    )
    return resp


@app.post("/generate-study-guide-multipart", response_model=GenerateStudyGuideResponse)
async def generate_study_guide_multipart(
    role: str = Form(...),
    years_experience: float = Form(...),
    study_plan_duration_days: int | None = Form(None),
    session_id: str | None = Form(None),
    job_description_text: str | None = Form(None),
    job_description_url: str | None = Form(None),
    resume_file: UploadFile | None = File(None),
    include_pdf: bool = Form(False),
):
    """
    Multipart variant that accepts an uploaded resume file.
    The server will extract raw text bytes (no OCR). For PDFs, this is usually
    insufficient for production; plug in a real PDF/DOCX text extractor.
    """
    resume_text = None
    if resume_file is not None:
        content_bytes = await resume_file.read()
        try:
            resume_text = content_bytes.decode("utf-8", errors="ignore")
        except Exception:
            resume_text = ""

    ui = UserInput(
        role=role,
        years_experience=years_experience,
        resume_text=resume_text,
        job_description_text=job_description_text,
        job_description_url=job_description_url,
        study_plan_duration_days=study_plan_duration_days,
        session_id=session_id,
    )

    resp = await controller_agent.generate_study_guide(
        user_input=ui, include_pdf=include_pdf
    )
    return resp


@app.post("/download-study-guide-pdf")
async def download_study_guide_pdf(user_input: UserInput):
    """
    Generate a study guide and return the PDF as a downloadable file.

    Same request body as POST /generate-study-guide. Returns a PDF file
    with Content-Disposition: attachment for direct saving.
    """
    resp = await controller_agent.generate_study_guide(
        user_input=user_input, include_pdf=False
    )
    html = resp.document.html
    pdf_bytes = html_to_pdf_bytes(html)

    if pdf_bytes is None:
        raise HTTPException(
            status_code=503,
            detail="PDF generation failed. Ensure xhtml2pdf is installed: pip install xhtml2pdf",
        )

    safe_role = "".join(c if c.isalnum() or c in " -_" else "_" for c in user_input.role)
    filename = f"InterviewPrepAI_{safe_role.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "app": settings.app_name})



