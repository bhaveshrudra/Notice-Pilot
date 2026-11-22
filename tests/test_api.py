import pytest
from tests.conftest import WORKSHOP_NOTICE

class TestAPI:
    # Test health endpoint
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "NoticePilot"
    
    # Test analyze endpoint with valid input
    def test_analyze_valid_notice(self, client):
        response = client.post("/api/analyze", json={"text": WORKSHOP_NOTICE, "use_ai": False})
        assert response.status_code == 200
        data = response.json()
        assert "extracted_info" in data
        assert "tasks" in data
        assert "summary" in data
        assert data["extraction_method"] == "local"
    
    # Test analyze with empty input
    def test_analyze_empty_input(self, client):
        response = client.post("/api/analyze", json={"text": "", "use_ai": False})
        assert response.status_code == 422  # Validation error
    
    # Test analyze with oversized input
    def test_analyze_oversized_input(self, client):
        response = client.post("/api/analyze", json={"text": "x" * 10001, "use_ai": False})
        assert response.status_code == 422
    
    # Test ICS export
    def test_ics_export(self, client):
        response = client.post("/api/export/ics", json={
            "title": "Test Event",
            "date": "2026-12-15",
            "time": "9:00 AM",
            "location": "Room 101",
            "description": "Test description"
        })
        assert response.status_code == 200
        assert "VCALENDAR" in response.text
        assert "VEVENT" in response.text
        assert "Test Event" in response.text
    
    # Test WhatsApp summary
    def test_whatsapp_summary(self, client):
        response = client.post("/api/share/whatsapp", json={
            "extracted_info": {"title": "Test Event", "date": "2026-12-15", "time": "9:00 AM", "location": "Room 101"},
            "tasks": [{"name": "Register", "deadline": "2026-12-10", "priority": "high"}]
        })
        assert response.status_code == 200
        data = response.json()
        assert "summary" in data
        assert len(data["summary"]) > 0
        assert "• Register (by 2026-12-10)" in data["summary"]
    
    # Test Gemini status
    def test_gemini_status(self, client):
        response = client.get("/api/gemini-status")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
    
    # Test ICS export all-day event
    def test_ics_allday_export(self, client):
        response = client.post("/api/export/ics", json={
            "title": "All Day Event",
            "date": "2026-12-15",
            "description": "Full day",
            "all_day": True
        })
        assert response.status_code == 200
        assert "VCALENDAR" in response.text

    # Test ICS export rejection on missing date
    def test_ics_export_missing_date(self, client):
        response = client.post("/api/export/ics", json={
            "title": "Date Missing Event",
            "date": None,
            "description": "No date provided"
        })
        assert response.status_code == 400
        assert "valid event date is required" in response.json()["detail"].lower()

    # Test ICS export rejection on empty string date
    def test_ics_export_empty_date(self, client):
        response = client.post("/api/export/ics", json={
            "title": "Empty Date Event",
            "date": "   ",
            "description": "Empty date string"
        })
        assert response.status_code == 400
        assert "valid event date is required" in response.json()["detail"].lower()

    # Test ICS export rejection on invalid date
    def test_ics_export_invalid_date(self, client):
        response = client.post("/api/export/ics", json={
            "title": "Invalid Date Event",
            "date": "invalid-non-date-xyz",
            "description": "Corrupted date"
        })
        assert response.status_code == 400
        assert "unable to parse" in response.json()["detail"].lower() or "invalid date" in response.json()["detail"].lower()

    # Test analyze with whitespace only
    def test_analyze_whitespace_only(self, client):
        response = client.post("/api/analyze", json={"text": "   \n\t  ", "use_ai": False})
        assert response.status_code == 422

    # Test health response adheres to HealthResponse model
    def test_health_response_schema(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"status", "service", "gemini_available"}
        assert isinstance(data["gemini_available"], bool)

    # Test gemini-status response adheres to GeminiStatusResponse model
    def test_gemini_status_schema(self, client):
        response = client.get("/api/gemini-status")
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"available"}
        assert isinstance(data["available"], bool)

    # Test share whatsapp response adheres to ShareResponse model
    def test_share_response_schema(self, client):
        response = client.post("/api/share/whatsapp", json={
            "extracted_info": {"title": "Annual Fest 2026", "date": "2026-12-20"},
            "tasks": ["Attend event"]
        })
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == {"summary"}
        assert "Annual Fest 2026" in data["summary"]

    # Test CORS headers for production onrender domain
    def test_cors_headers_render_origin(self, client):
        headers = {
            "Origin": "https://noticepilot.onrender.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
        response = client.options("/api/analyze", headers=headers)
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "https://noticepilot.onrender.com"
