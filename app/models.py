from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import uuid

class NoticeInput(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000, description="Notice text to analyze")
    use_ai: bool = False
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        v = v.strip()
        if not v:
            raise ValueError('Notice text cannot be empty')
        if len(v) > 10000:
            raise ValueError('Notice text exceeds maximum limit of 10,000 characters')
        return v

class EvidenceSnippet(BaseModel):
    field: str
    snippet: str  
    confidence: float = Field(ge=0.0, le=1.0)

class ExtractedInfo(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    registration_deadline: Optional[str] = None
    requirements: List[str] = Field(default_factory=list)
    contact_info: List[str] = Field(default_factory=list)
    action_items: List[str] = Field(default_factory=list)
    evidence: List[EvidenceSnippet] = Field(default_factory=list)
    uncertain_fields: List[str] = Field(default_factory=list)

class TaskItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    deadline: Optional[str] = None
    priority: str = "medium"
    completed: bool = False
    description: str = ""

class AnalysisResponse(BaseModel):
    extracted_info: ExtractedInfo
    tasks: List[TaskItem] = Field(default_factory=list)
    summary: str
    extraction_method: str

class CalendarExportRequest(BaseModel):
    title: str
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    description: str = ""
    all_day: bool = False

class ShareRequest(BaseModel):
    extracted_info: dict = Field(default_factory=dict)
    tasks: list = Field(default_factory=list)
