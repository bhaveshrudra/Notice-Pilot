# 🧭 NoticePilot

> **From Notice to Action** — Transforming messy, unstructured campus notices into crystal-clear tasks, calendar events, and reminders in seconds.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Pytest-Passing-green?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

---

## 🌟 Introduction

In academic institutions and organizations, critical operational information is routinely dispersed as chaotic wall-of-text circulars, PDF announcements, WhatsApp forwards, or urgent emails. 

**NoticePilot** bridges the gap between passive announcements and proactive execution. It parses unstructured text, extracts verified dates, times, venues, and registration deadlines, auto-generates prioritizeable task checklists, exports standards-compliant iCalendar files (`.ics`), and prepares formatted WhatsApp summaries — all with full transparency and zero hallucinated dates.

---

## 🎯 Problem Statement

Every semester, thousands of students miss vital opportunities:
- ❌ **Buried Deadlines:** Critical scholarship, exam form, or hackathon deadlines get lost inside multi-paragraph notices.
- ❌ **Cognitive Overload:** Students receive dozens of notifications across multiple fragmented channels daily.
- ❌ **Friction to Action:** Manually transferring dates from circulars into personal Google or Apple calendars takes effort, leading to procrastination and forgotten obligations.
- ❌ **Context Blindness:** Notices often leave students wondering *"What exact steps do I need to take right now to prepare?"*

**NoticePilot** solves this by converting unstructured announcement text into structured, actionable data in a single click.

---

## ✨ Features (The Core 8)

NoticePilot provides an integrated, end-to-end workflow suite:

1. 📝 **Notice Input**:
   - Paste any raw text notice, circular, syllabus announcement, or email.
   - Quick-load pre-configured sample templates (Technical Workshop, Guest Lecture, Semester Exam) to test instantly.
   - Character count monitoring with robust client and server validation limits (up to 10,000 characters).

2. 🧠 **Smart Extraction**:
   - **Dual-Engine Architecture**: Employs a robust, deterministic local extraction engine (regex, pattern matchers, and structural heuristics) that runs offline with zero API latency.
   - **Optional AI Enhancement**: Seamlessly integrates with Google Gemini AI (`gemini-1.5-flash` / `gemini-pro`) when an API key is provided, gracefully falling back to local extraction if unavailable.
   - **Integrity Rule**: Never hallucinates or invents dates. If a date is absent or ambiguous, it is either flagged in `uncertain_fields` or omitted with an honest confidence score.

3. ✅ **Task Generation**:
   - Translates notice requirements into prioritized, bite-sized tasks (`high`, `medium`, `low`).
   - Automatically assigns targeted deadlines (e.g., registration cutoff dates, submission targets).
   - Allows students to toggle tasks as completed or edit them directly on the fly.

4. ⏱️ **Deadline Dashboard**:
   - Real-time countdown timers and visual urgency indicators (Urgent / Approaching / Normal).
   - Live visual feedback that highlights pressing deadlines before they slip away.

5. 📅 **Calendar Export**:
   - One-click `.ics` (iCalendar) generation compatible with **Google Calendar**, **Apple Calendar**, **Microsoft Outlook**, and mobile calendars.
   - Supports both precise scheduled time slots (with start and end times) and all-day multi-day event spans.

6. 💬 **Smart Sharing**:
   - Generates cleanly formatted, emoji-enhanced bullet summaries optimized for WhatsApp, Telegram, Discord, and student group chats.
   - Instant "Copy to Clipboard" and `https://wa.me/` direct dispatch.

7. 🔍 **Extraction Explanation**:
   - Complete audit trail for transparency: displays confidence scores (0.0 – 1.0) for every extracted field.
   - Shows **evidence snippets** highlighting the exact sentence or phrase from the notice that justified each extracted value.

8. 📜 **History**:
   - 100% privacy-first local history powered by browser `LocalStorage`.
   - Re-visit previously analyzed notices, review extracted tasks, and re-export calendar events without sending data to an external database.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, Uvicorn |
| **Extraction** | Deterministic Regex & Rule-Based Heuristic Parser + Optional Google Gemini API |
| **Frontend** | Modern Vanilla JavaScript (ES6+), HTML5 Semantic markup, Modern CSS3 (Glassmorphism & Responsive Design) |
| **Storage** | Client-Side `LocalStorage` (Zero data retention on server, privacy-first) |
| **Testing** | Pytest, HTTPX, FastAPI TestClient |
| **Containerization** | Docker (Alpine/Debian-slim multi-stage, non-root security) |
| **Cloud Target** | Google Cloud Run / Container Apps (stateless, auto-scaling) |

---

## 🏗️ Architecture

NoticePilot follows a modular, client-server architecture designed for lightning-fast responsiveness, zero configuration requirements, and fail-safe operation:

```
┌────────────────────────────────────────────────────────┐
│                   Frontend (Client)                    │
│   Vanilla JS + Modern CSS + LocalStorage Notice Store  │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP POST / GET (JSON)
                           ▼
┌────────────────────────────────────────────────────────┐
│               NoticePilot FastAPI Backend              │
│  ┌────────────────────┐       ┌──────────────────────┐ │
│  │   /api/analyze     │       │   /api/export/ics    │ │
│  │  Input Validation  │       │   RFC 5545 Generator │ │
│  └─────────┬──────────┘       └──────────────────────┘ │
│            │                                           │
│            ├──► [Optional Gemini API] (If configured)  │
│            │          │ (Fallback on failure / absent) │
│            ▼          ▼                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │   Deterministic Local Extraction Engine          │  │
│  │   - Regex Date/Time Parsers (ISO, DD/MM, words)  │  │
│  │   - Venue & Location Heuristics                  │  │
│  │   - Contact & Email Extractors                   │  │
│  │   - Task & Requirement Synthesizers              │  │
│  │   - Evidence & Confidence Score Generator        │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Installation

### Prerequisites
- Python 3.11 or higher
- `git`
- (Optional) Docker

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/NoticePilot.git
cd NoticePilot
```

### 2. Create and Activate a Virtual Environment
**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💻 Running Locally

Start the development server using `uvicorn`:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Once started:
- 🌐 **Web Interface:** Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.
- 📚 **Interactive Swagger API Docs:** Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
- 🩺 **Health Check:** Open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

---

## 🧪 Testing

NoticePilot includes a comprehensive Pytest test suite covering deterministic extraction, edge cases, date normalization, and API routes.

Run the test suite:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run with test coverage report:
```bash
pytest --cov=app --cov-report=term-missing
```

### What the Tests Cover:
- ✅ **Date & Time Variations:** ISO (`2026-12-15`), slash formats (`28/11/2026`), and written ordinal dates (`15th December 2026`).
- ✅ **Honest No-Date Handling:** Verifies that missing dates are never fabricated (`no-hallucination` guarantee).
- ✅ **Task & Priority Derivation:** Verifies proper generation of actionable tasks with valid UUIDs and priorities (`high`, `medium`, `low`).
- ✅ **API Contract & Validation:** Tests boundary conditions (empty text, inputs exceeding 10,000 characters, missing keys).
- ✅ **ICS Spec Compliance:** Checks iCalendar header markers (`VCALENDAR`, `VEVENT`, timestamps).
- ✅ **WhatsApp Summary Generation:** Confirms summary layout and information density.

---

## 🐳 Docker & Cloud Deployment

### 1. Build Docker Image
```bash
docker build -t noticepilot:latest .
```

### 2. Run Container Locally
```bash
docker run -p 8000:8000 -e PORT=8000 noticepilot:latest
```
Access the application at [http://localhost:8000](http://localhost:8000).

### 3. Deploy to Google Cloud Run
NoticePilot is built ready for stateless serverless deployment on Google Cloud Run:

```bash
# Set your GCP Project ID
export PROJECT_ID="your-gcp-project-id"

# Build and push using Google Cloud Build
gcloud builds submit --tag gcr.io/${PROJECT_ID}/noticepilot

# Deploy to Cloud Run
gcloud run deploy noticepilot \
    --image gcr.io/${PROJECT_ID}/noticepilot \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars="PORT=8080"
```

---

## ⚙️ Environment Variables

NoticePilot works completely out-of-the-box with **zero required environment variables**. Optional variables can be configured via a `.env` file or container environment:

| Variable | Type | Default | Description |
|---|---|---|---|
| `PORT` | Integer | `8000` | Port on which the Uvicorn ASGI server listens |
| `GEMINI_API_KEY` | String | *(None)* | Optional Google Gemini API key to enable experimental AI extraction mode |

---

## 📖 API Documentation

All endpoints accept and return JSON unless specified otherwise.

| Method | Endpoint | Description | Request Body / Params | Response |
|---|---|---|---|---|
| `GET` | `/health` | System health status & Gemini availability | None | `{"status": "healthy", "service": "NoticePilot", "gemini_available": bool}` |
| `POST` | `/api/analyze` | Parse notice text and extract structured information | `{"text": str, "use_ai": bool}` | `AnalysisResponse` (Extracted info, tasks, summary, evidence) |
| `POST` | `/api/export/ics` | Generate downloadable `.ics` calendar file | `CalendarExportRequest` (title, date, time, location, etc.) | Raw `text/calendar` attachment |
| `POST` | `/api/share/whatsapp` | Generate pre-formatted WhatsApp share message | `ShareRequest` (extracted_info, tasks) | `{"summary": str}` |
| `GET` | `/api/gemini-status`| Check if Gemini AI model is currently accessible | None | `{"available": bool}` |

---

## 🔒 Security Considerations

- **Strict Input Validation:** Enforces character count constraints (1 to 10,000 characters) via Pydantic schemas to prevent denial-of-service (DoS) via payload flooding.
- **Client-Side Privacy:** No student notices or extracted tasks are saved in a persistent database. Text stays in the browser's `LocalStorage` and volatile request lifecycles.
- **XSS Sanitization:** Frontend renders untrusted notice content using safe text assignment (`textContent` and parameterized DOM building) to block script injection.
- **Non-Root Container Execution:** The `Dockerfile` provisions an unprivileged user (`appuser`) to execute the application process, preventing container breakout risks.

---

## ⚠️ Known Limitations

- **Local Extraction Heuristics:** The deterministic parser is tuned for standard Indian and international collegiate circular formats. Non-standard abbreviations or unconventional date syntaxes may be categorized under `uncertain_fields`.
- **Stateless Storage:** Clearing browser cache or switching devices will reset the history list, as data is kept strictly client-side for privacy.

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).

---

*Crafted with ❤️ for students everywhere by the NoticePilot Team.*
