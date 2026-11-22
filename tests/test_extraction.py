import pytest
from app.extraction import extract_from_notice, generate_tasks, generate_summary
from app.models import ExtractedInfo
from tests.conftest import WORKSHOP_NOTICE, GUEST_LECTURE_NOTICE, EXAM_NOTICE, MINIMAL_NOTICE, NO_DATE_NOTICE

class TestExtraction:
    # Test 1: Workshop notice extracts title
    def test_extract_title_from_workshop(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert result.title is not None
        assert len(result.title) > 0
    
    # Test 2: Workshop notice extracts date in proper format
    def test_extract_date_format(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert result.date is not None
        assert "2026" in result.date
        # Should contain December 15 info
    
    # Test 3: Extracts time
    def test_extract_time(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert result.time is not None
        assert "AM" in result.time.upper() or "9" in result.time
    
    # Test 4: Extracts location/venue
    def test_extract_location(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert result.location is not None
        assert "Seminar Hall" in result.location or "Block A" in result.location
    
    # Test 5: Extracts registration deadline
    def test_extract_registration_deadline(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert result.registration_deadline is not None
        assert "2026" in result.registration_deadline
    
    # Test 6: Extracts contact info (email)
    def test_extract_contact_email(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert len(result.contact_info) > 0
        assert any("@" in c for c in result.contact_info)
    
    # Test 7: Extracts requirements
    def test_extract_requirements(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert len(result.requirements) > 0
    
    # Test 8: DD/MM/YYYY date format
    def test_dd_mm_yyyy_format(self):
        result = extract_from_notice(GUEST_LECTURE_NOTICE)
        assert result.date is not None
    
    # Test 9: Multiple deadlines in exam notice
    def test_multiple_deadlines_exam(self):
        result = extract_from_notice(EXAM_NOTICE)
        assert result.date is not None or result.registration_deadline is not None
        # Should extract at least some dates
    
    # Test 10: Missing date notice
    def test_no_date_notice(self):
        result = extract_from_notice(NO_DATE_NOTICE)
        # Should NOT invent a date
        # Date might be None or the field should be in uncertain_fields
        # The key rule: never invent dates
        assert result.date is None or "date" in result.uncertain_fields
    
    # Test 11: Empty input
    def test_empty_input(self):
        result = extract_from_notice("")
        assert result.title is None or result.title == ""
        assert result.date is None
    
    # Test 12: Evidence snippets are generated
    def test_evidence_snippets(self):
        result = extract_from_notice(WORKSHOP_NOTICE)
        assert len(result.evidence) > 0
        # Each evidence should have field, snippet, confidence
        for ev in result.evidence:
            assert ev.field
            assert ev.snippet
            assert 0.0 <= ev.confidence <= 1.0
    
    # Test 13: Task generation from extraction
    def test_task_generation(self):
        info = extract_from_notice(WORKSHOP_NOTICE)
        tasks = generate_tasks(info)
        assert len(tasks) > 0
        for task in tasks:
            assert task.name
            assert task.priority in ["high", "medium", "low"]
            assert task.id  # UUID
    
    # Test 14: Summary generation
    def test_summary_generation(self):
        info = extract_from_notice(WORKSHOP_NOTICE)
        summary = generate_summary(info)
        assert len(summary) > 0
        assert isinstance(summary, str)
    
    # Test 15: Minimal notice extraction
    def test_minimal_notice(self):
        result = extract_from_notice(MINIMAL_NOTICE)
        # Should extract something but not invent
        assert isinstance(result, ExtractedInfo)

    # Test 16: Ambiguous numeric date detection
    def test_ambiguous_numeric_date(self):
        ambiguous_notice = "Department Seminar will take place on 05/06/2026 at Seminar Hall."
        result = extract_from_notice(ambiguous_notice)
        assert result.date is not None
        assert "date" in result.uncertain_fields

    # Test 17: Calendar export rejects missing date
    def test_calendar_export_missing_date_exception(self):
        from app.calendar_export import generate_ics
        with pytest.raises(ValueError, match="valid event date is required"):
            generate_ics(title="No Date Event", date_str=None)
        with pytest.raises(ValueError, match="valid event date is required"):
            generate_ics(title="Blank Date Event", date_str="   ")

    # Test 18: Calendar export rejects invalid date
    def test_calendar_export_invalid_date_exception(self):
        from app.calendar_export import generate_ics
        with pytest.raises(ValueError, match="Unable to parse event date"):
            generate_ics(title="Invalid Date Event", date_str="not-a-valid-date-str")

    # Test 19: Calendar ICS escaping for RFC 5545 special characters
    def test_calendar_ics_escaping(self):
        from app.calendar_export import generate_ics
        ics = generate_ics(
            title="AI, ML; Seminar \\ Workshop",
            date_str="2026-12-15",
            location="Room 101, Block A; Wing B",
            description="First line\nSecond line; with comma, and backslash\\"
        )
        assert r"AI\, ML\; Seminar \\ Workshop" in ics
        assert r"Room 101\, Block A\; Wing B" in ics
        assert r"\n" in ics

    # Test 20: Calendar ICS line folding (> 75 octets)
    def test_calendar_ics_line_folding(self):
        from app.calendar_export import generate_ics
        long_title = "A" * 90
        ics = generate_ics(title=long_title, date_str="2026-12-15")
        # Ensure CRLF followed by space line folding occurred
        assert "\r\n " in ics
        for line in ics.split("\r\n"):
            assert len(line.encode("utf-8")) <= 75

    # Test 21: Dynamic priority calculation relative to today
    def test_dynamic_priority_calculation(self):
        import datetime
        from app.extraction import _calculate_priority
        today = datetime.date.today()
        soon = (today + datetime.timedelta(days=2)).isoformat()
        medium = (today + datetime.timedelta(days=5)).isoformat()
        far = (today + datetime.timedelta(days=25)).isoformat()
        
        assert _calculate_priority(soon) == "high"
        assert _calculate_priority(medium) == "medium"
        assert _calculate_priority(far) == "low"

    # Test 22: Never invent missing fields
    def test_never_invent_missing_fields(self):
        sparse_notice = "Meeting at 4:00 PM."
        result = extract_from_notice(sparse_notice)
        assert result.date is None
        assert result.location is None
        assert result.registration_deadline is None

    # Test 23: Virtual location & platform extraction (Zoom, Google Meet, Teams)
    def test_extract_virtual_location_and_platform(self):
        notice = """
        Webinar on Cloud Computing
        Platform: Google Meet
        Date: 10th December 2026
        Time: 5:00 PM
        """
        result = extract_from_notice(notice)
        assert result.location is not None
        assert "Google Meet" in result.location

        notice2 = "Interactive Q&A Session conducted via Zoom on 12th December 2026 at 4:00 PM."
        result2 = extract_from_notice(notice2)
        assert result2.location is not None
        assert "Zoom" in result2.location

    # Test 24: Fee and deadline imperative action items
    def test_fee_deadline_imperative_action_item(self):
        notice = """
        CIRCULAR: Semester Fee Payment
        Date: 20th November 2026
        Last date to pay tuition fee: 30th November 2026
        Students must clear all library dues before payment.
        """
        result = extract_from_notice(notice)
        assert any("pay tuition fee" in a.lower() for a in result.action_items)
        assert any("clear all library dues" in a.lower() for a in result.action_items)

    # Test 25: Comprehensive campus placement / internship notice
    def test_internship_placement_notice(self):
        notice = """
        CAMPUS PLACEMENT DRIVE: Google Software Engineering Internship 2027
        Eligibility: 6th Semester B.Tech CSE / IT with CGPA >= 8.0
        Package: INR 1.2 Lakh / month stipend
        Online Coding Test Date: 18th December 2026
        Registration deadline: 12th December 2026
        Venue: Online via HackerRank
        Contact: placement@college.edu
        Please submit your updated resume via the portal.
        """
        result = extract_from_notice(notice)
        assert result.title is not None and "Placement" in result.title or "Google" in result.title
        assert result.date == "2026-12-18"
        assert result.registration_deadline == "2026-12-12"
        assert "HackerRank" in result.location or "Online" in result.location
        assert "placement@college.edu" in result.contact_info
        assert any("resume" in a.lower() for a in result.action_items)

    # Test 26: TaskItem priority normalization and fallback
    def test_task_item_priority_normalization(self):
        from app.models import TaskItem
        t1 = TaskItem(name="Task 1", priority="HIGH")
        assert t1.priority == "high"
        t2 = TaskItem(name="Task 2", priority="UNKNOWN_URGENCY")
        assert t2.priority == "medium"
