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
