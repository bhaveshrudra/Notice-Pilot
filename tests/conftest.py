import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
def client():
    """Synchronous test client using httpx."""
    from fastapi.testclient import TestClient
    return TestClient(app)

# Sample notice texts for testing
WORKSHOP_NOTICE = """Subject: Technical Workshop on AI & Machine Learning

The Department of Computer Science is organizing a Technical Workshop on "Artificial Intelligence & Machine Learning".

Date: 15th December 2026
Time: 9:00 AM to 5:00 PM
Venue: Seminar Hall, Block A, 3rd Floor

Registration deadline: 10th December 2026

Requirements:
- Bring your own laptop with Python 3.8+ installed
- Students must carry their college ID card

Contact: Dr. Priya Sharma - priya.sharma@college.edu - 9876543210"""

GUEST_LECTURE_NOTICE = """NOTICE

A Guest Lecture on "Cybersecurity in the Age of AI" will be conducted.

Speaker: Mr. Rajesh Kumar, CSO, Infosys

Date of Lecture: 28/11/2026
Time: 2:00 PM - 4:00 PM
Venue: Auditorium, Main Building

Students are required to:
1. Carry a notebook and pen
2. Submit a one-page report within 3 days
3. Dress code: Formal attire

Email: tnp@college.edu
Phone: 011-2345-6789"""

EXAM_NOTICE = """EXAMINATION NOTICE

End Semester Examinations will commence:

Examination Period: 1st December 2026 to 15th December 2026
Reporting Time: 9:30 AM

Important Deadlines:
- Last date to pay examination fee: 25th November 2026
- Last date for exam form submission: 23rd November 2026

Instructions:
- Students must carry their hall ticket and college ID
- Use of electronic devices is strictly prohibited

Contact: examcell@college.edu, Phone: 011-9876-5432"""

MINIMAL_NOTICE = """Meeting tomorrow at 3 PM in Room 101."""

NO_DATE_NOTICE = """Important: All students must submit their project reports to the department office. Contact prof@college.edu for details."""
