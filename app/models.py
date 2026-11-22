"""
Pydantic data schemas for NoticePilot.
Defines strict input validation, extraction responses, task entities, and export requests.
"""

from typing import Any, Dict, List, Literal, Optional, Union
import uuid
from pydantic import BaseModel, Field, field_validator


class NoticeInput(BaseModel):
    """Input payload for notice text analysis."""
    text: str = Field(..., min_length=1, max_length=10000, description="Notice text to analyze")
    use_ai: bool = Field(default=False, description="Whether to request optional Gemini-assisted analysis")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError('Notice text cannot be empty or purely whitespace')
        if len(cleaned) > 10000:
            raise ValueError('Notice text exceeds maximum limit of 10,000 characters')
        return cleaned


class EvidenceSnippet(BaseModel):
    """Quotation evidence with confidence scoring for an extracted field."""
    field: str = Field(..., description="Field name for which evidence was found")
    snippet: str = Field(..., description="Exact textual excerpt from the source notice")
    confidence: float = Field(ge=0.0, le=1.0, description="Extraction confidence score between 0.0 and 1.0")


class ExtractedInfo(BaseModel):
    """Structured fields extracted from unstructured notice text."""
    title: Optional[str] = Field(default=None, description="Event or announcement title")
    date: Optional[str] = Field(default=None, description="Event commencement date in ISO YYYY-MM-DD")
    time: Optional[str] = Field(default=None, description="Event timing or schedule range")
    location: Optional[str] = Field(default=None, description="Physical venue or virtual platform")
    registration_deadline: Optional[str] = Field(default=None, description="Registration or submission deadline in ISO YYYY-MM-DD")
    requirements: List[str] = Field(default_factory=list, description="Eligibility, prerequisites, or required items")
    contact_info: List[str] = Field(default_factory=list, description="Extracted emails, phone numbers, or coordinators")
    action_items: List[str] = Field(default_factory=list, description="Immediate tasks for students")
    evidence: List[EvidenceSnippet] = Field(default_factory=list, description="Supporting evidence quotes from notice")
    uncertain_fields: List[str] = Field(default_factory=list, description="Fields flagged for manual review")


class TaskItem(BaseModel):
    """Actionable task derived from notice deadlines or user input."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique task identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Brief task summary")
    deadline: Optional[str] = Field(default=None, description="ISO date or deadline string")
    priority: Literal["high", "medium", "low"] = Field(default="medium", description="Task urgency tier")
    completed: bool = Field(default=False, description="Completion toggle state")
    description: str = Field(default="", description="Detailed instructions or context")

    @field_validator('priority', mode='before')
    @classmethod
    def normalize_priority(cls, v: Any) -> str:
        if isinstance(v, str):
            v_clean = v.strip().lower()
            if v_clean in ("high", "medium", "low"):
                return v_clean
        return "medium"


class AnalysisResponse(BaseModel):
    """Complete structured response from notice analysis."""
    extracted_info: ExtractedInfo
    tasks: List[TaskItem] = Field(default_factory=list)
    summary: str
    extraction_method: str = Field(description="Engine used: 'local' or 'gemini'")


class CalendarExportRequest(BaseModel):
    """Request payload for RFC 5545 iCalendar generation."""
    title: str = Field(default="College Notice Event", min_length=1, max_length=255)
    date: Optional[str] = Field(default=None, description="Event date (strictly required for valid ICS)")
    time: Optional[str] = Field(default=None, description="Event time or range")
    location: Optional[str] = Field(default=None, description="Venue or platform")
    description: str = Field(default="", max_length=5000, description="Event notes or summary")
    all_day: bool = Field(default=False, description="Whether event is all-day")


class ShareRequest(BaseModel):
    """Request payload for WhatsApp summary formatting."""
    extracted_info: Dict[str, Any] = Field(default_factory=dict)
    tasks: List[Union[TaskItem, Dict[str, Any], str]] = Field(default_factory=list)


class ShareResponse(BaseModel):
    """Formatted WhatsApp-ready text summary."""
    summary: str


class HealthResponse(BaseModel):
    """Service health check response schema."""
    status: str = "healthy"
    service: str = "NoticePilot"
    gemini_available: bool = False


class GeminiStatusResponse(BaseModel):
    """Availability status of Google Gemini API key."""
    available: bool
