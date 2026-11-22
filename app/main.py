import os
import re
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response, JSONResponse

from app.models import (
    NoticeInput,
    AnalysisResponse,
    ExtractedInfo,
    CalendarExportRequest,
    ShareRequest
)
from app.extraction import extract_from_notice, generate_tasks, generate_summary
from app.calendar_export import generate_ics
from app.gemini_service import is_gemini_available, extract_with_gemini

app = FastAPI(
    title="NoticePilot",
    version="1.0.0",
    description="Smart workflow automation platform converting college notices into actionable tasks and calendar events"
)

# Enable CORS for local development and cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static folder exists
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "NoticePilot",
        "gemini_available": is_gemini_available()
    }


@app.get("/api/gemini-status")
async def gemini_status():
    """Returns whether Gemini API key is configured."""
    return {"available": is_gemini_available()}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_notice(payload: NoticeInput):
    """
    Analyze notice text using deterministic local regex engine or optional Gemini AI.
    Returns extracted structured info, generated tasks, and summary.
    """
    try:
        extraction_method = "local"
        extracted_info = None

        if payload.use_ai and is_gemini_available():
            try:
                gemini_data = await extract_with_gemini(payload.text)
                if gemini_data:
                    extracted_info = ExtractedInfo(**gemini_data)
                    extraction_method = "gemini"
            except Exception:
                extracted_info = None

        # Fallback or primary local deterministic extraction
        if not extracted_info:
            extracted_info = extract_from_notice(payload.text)
            extraction_method = "local"

        tasks = generate_tasks(extracted_info)
        summary = generate_summary(extracted_info)

        return AnalysisResponse(
            extracted_info=extracted_info,
            tasks=tasks,
            summary=summary,
            extraction_method=extraction_method
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing notice: {str(e)}")


@app.post("/api/export/ics")
async def export_ics(payload: CalendarExportRequest):
    """
    Export event as an RFC 5545 compliant iCalendar (.ics) file.
    """
    try:
        ics_text = generate_ics(
            title=payload.title,
            date_str=payload.date,
            time_str=payload.time,
            location=payload.location,
            description=payload.description,
            all_day=payload.all_day
        )
        safe_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', payload.title[:30]).strip('_') or "notice_event"
        return Response(
            content=ics_text,
            media_type="text/calendar",
            headers={
                "Content-Disposition": f'attachment; filename="{safe_filename}.ics"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate ICS file: {str(e)}")


@app.post("/api/share/whatsapp")
async def share_whatsapp(payload: ShareRequest):
    """
    Generate a WhatsApp-formatted summary string with markdown asterisks and bullet points.
    """
    try:
        info = payload.extracted_info
        title = info.get("title") or "Notice Update"
        date = info.get("date") or "TBD"
        time_val = info.get("time") or "TBD"
        location = info.get("location") or "TBD"
        deadline = info.get("registration_deadline")

        lines = [
            f"📢 *{title}*",
            f"📅 *Date:* {date}",
            f"⏰ *Time:* {time_val}",
            f"📍 *Venue:* {location}",
        ]
        if deadline:
            lines.append(f"⏳ *Registration Deadline:* {deadline}")

        tasks = payload.tasks
        if tasks:
            lines.append("\n✅ *Action Items:*")
            for t in tasks:
                if isinstance(t, dict):
                    name = t.get("name", "")
                    d = t.get("deadline")
                    item = f"• {name}"
                    if d:
                        item += f" (by {d})"
                    lines.append(item)
                elif isinstance(t, str):
                    lines.append(f"• {t}")

        contact = info.get("contact_info")
        if contact and isinstance(contact, list) and len(contact) > 0:
            lines.append(f"\n📞 *Contact:* {', '.join(contact)}")

        lines.append("\n_Created with NoticePilot_")
        return {"summary": "\n".join(lines)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate WhatsApp summary: {str(e)}")


@app.get("/")
async def root():
    """Serve frontend index.html if present, else provide service status."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({
        "service": "NoticePilot API",
        "version": "1.0.0",
        "status": "online",
        "docs_url": "/docs"
    })


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
