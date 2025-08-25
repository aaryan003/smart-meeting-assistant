from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class MeetingStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class SummaryType(str, Enum):
    QUICK = "QUICK"
    DETAILED = "DETAILED"
    ACTION_FOCUSED = "ACTION_FOCUSED"

class ActionPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class ActionItemStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# Request Models
class CreateMeetingRequest(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    meeting_url: Optional[str] = None
    organizer_email: str

    @validator('title')
    def validate_title(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Meeting title cannot be empty')
        return v.strip()

class UpdateMeetingRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    meeting_url: Optional[str] = None
    status: Optional[MeetingStatus] = None

class AddParticipantRequest(BaseModel):
    name: str
    email: Optional[EmailStr] = None

class TranscriptChunk(BaseModel):
    speaker: Optional[str] = None
    content: str
    start_time: float
    end_time: float
    confidence: Optional[float] = None

class CreateSummaryRequest(BaseModel):
    type: SummaryType = SummaryType.QUICK

class CreateActionItemRequest(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_email: Optional[str] = None
    priority: ActionPriority = ActionPriority.MEDIUM
    due_date: Optional[datetime] = None

# Response Models
class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    avatar: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class MeetingParticipantResponse(BaseModel):
    id: str
    name: str
    email: Optional[str]
    joined_at: Optional[datetime]
    left_at: Optional[datetime]

    class Config:
        from_attributes = True

class TranscriptResponse(BaseModel):
    id: str
    speaker: Optional[str]
    content: str
    start_time: float
    end_time: float
    confidence: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True

class SummaryResponse(BaseModel):
    id: str
    type: SummaryType
    content: str
    key_points: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ActionItemResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    priority: ActionPriority
    status: ActionItemStatus
    due_date: Optional[datetime]
    assignee: Optional[UserResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MeetingResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    status: MeetingStatus
    meeting_url: Optional[str]
    recording_url: Optional[str]
    organizer: UserResponse
    participants: List[MeetingParticipantResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MeetingDetailResponse(MeetingResponse):
    transcripts: List[TranscriptResponse] = []
    summaries: List[SummaryResponse] = []
    action_items: List[ActionItemResponse] = []

# WebSocket Models
class WSMessage(BaseModel):
    type: str
    data: dict
    timestamp: datetime = datetime.now()

class WSTranscriptionMessage(WSMessage):
    meeting_id: str
    speaker: Optional[str]
    content: str
    is_final: bool = False

# Utility Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int