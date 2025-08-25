from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.models.meeting import (
    CreateMeetingRequest,
    UpdateMeetingRequest,
    MeetingResponse,
    MeetingDetailResponse,
    APIResponse,
    AddParticipantRequest,
    MeetingParticipantResponse
)
from app.utils.database import get_db
from app.services.meeting_service import MeetingService

router = APIRouter()

@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    meeting_data: CreateMeetingRequest,
    db = Depends(get_db)
):
    """Create a new meeting"""
    try:
        meeting_service = MeetingService(db)
        meeting = await meeting_service.create_meeting(meeting_data)
        return meeting
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create meeting: {str(e)}")

@router.get("/", response_model=List[MeetingResponse])
async def list_meetings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    organizer_email: Optional[str] = None,
    db = Depends(get_db)
):
    """List all meetings with optional filtering"""
    try:
        meeting_service = MeetingService(db)
        meetings = await meeting_service.list_meetings(
            skip=skip,
            limit=limit,
            status=status,
            organizer_email=organizer_email
        )
        return meetings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch meetings: {str(e)}")

@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
async def get_meeting(
    meeting_id: str,
    include_transcripts: bool = Query(False),
    include_summaries: bool = Query(False),
    include_action_items: bool = Query(False),
    db = Depends(get_db)
):
    """Get detailed meeting information"""
    try:
        meeting_service = MeetingService(db)
        meeting = await meeting_service.get_meeting_details(
            meeting_id=meeting_id,
            include_transcripts=include_transcripts,
            include_summaries=include_summaries,
            include_action_items=include_action_items
        )
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
            
        return meeting
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch meeting: {str(e)}")

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: str,
    meeting_data: UpdateMeetingRequest,
    db = Depends(get_db)
):
    """Update meeting information"""
    try:
        meeting_service = MeetingService(db)
        meeting = await meeting_service.update_meeting(meeting_id, meeting_data)
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
            
        return meeting
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update meeting: {str(e)}")

@router.delete("/{meeting_id}")
async def delete_meeting(
    meeting_id: str,
    db = Depends(get_db)
):
    """Delete a meeting"""
    try:
        meeting_service = MeetingService(db)
        success = await meeting_service.delete_meeting(meeting_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Meeting not found")
            
        return APIResponse(
            success=True,
            message="Meeting deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete meeting: {str(e)}")

@router.post("/{meeting_id}/start")
async def start_meeting(
    meeting_id: str,
    db = Depends(get_db)
):
    """Start a meeting (change status to IN_PROGRESS)"""
    try:
        meeting_service = MeetingService(db)
        meeting = await meeting_service.start_meeting(meeting_id)
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
            
        return APIResponse(
            success=True,
            message="Meeting started successfully",
            data={"meeting_id": meeting_id, "started_at": meeting.started_at}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start meeting: {str(e)}")

@router.post("/{meeting_id}/end")
async def end_meeting(
    meeting_id: str,
    db = Depends(get_db)
):
    """End a meeting (change status to COMPLETED)"""
    try:
        meeting_service = MeetingService(db)
        meeting = await meeting_service.end_meeting(meeting_id)
        
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
            
        return APIResponse(
            success=True,
            message="Meeting ended successfully",
            data={"meeting_id": meeting_id, "ended_at": meeting.ended_at}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end meeting: {str(e)}")

@router.post("/{meeting_id}/participants", response_model=MeetingParticipantResponse)
async def add_participant(
    meeting_id: str,
    participant_data: AddParticipantRequest,
    db = Depends(get_db)
):
    """Add a participant to the meeting"""
    try:
        meeting_service = MeetingService(db)
        participant = await meeting_service.add_participant(meeting_id, participant_data)
        
        if not participant:
            raise HTTPException(status_code=404, detail="Meeting not found")
            
        return participant
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add participant: {str(e)}")

@router.get("/{meeting_id}/participants", response_model=List[MeetingParticipantResponse])
async def get_participants(
    meeting_id: str,
    db = Depends(get_db)
):
    """Get all participants of a meeting"""
    try:
        meeting_service = MeetingService(db)
        participants = await meeting_service.get_participants(meeting_id)
        return participants
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch participants: {str(e)}")