from typing import List, Optional
from datetime import datetime
from prisma import Prisma

from app.models.meeting import (
    CreateMeetingRequest,
    UpdateMeetingRequest,
    MeetingResponse,
    MeetingDetailResponse,
    AddParticipantRequest,
    MeetingParticipantResponse,
    MeetingStatus
)

class MeetingService:
    def __init__(self, db: Prisma):
        self.db = db

    async def create_meeting(self, meeting_data: CreateMeetingRequest) -> MeetingResponse:
        """Create a new meeting"""
        
        # First, ensure user exists or create one
        user = await self.db.user.upsert(
            where={'email': meeting_data.organizer_email},
            data={
                'create': {
                    'email': meeting_data.organizer_email,
                    'name': meeting_data.organizer_email.split('@')[0]  # Default name from email
                },
                'update': {}
            }
        )
        
        # Create the meeting
        meeting = await self.db.meeting.create(
            data={
                'title': meeting_data.title,
                'description': meeting_data.description,
                'scheduledAt': meeting_data.scheduled_at,
                'meetingUrl': meeting_data.meeting_url,
                'organizerId': user.id,
                'status': MeetingStatus.SCHEDULED
            },
            include={
                'organizer': True,
                'participants': True
            }
        )
        
        return MeetingResponse.from_orm(meeting)

    async def get_meeting_details(
        self,
        meeting_id: str,
        include_transcripts: bool = False,
        include_summaries: bool = False,
        include_action_items: bool = False
    ) -> Optional[MeetingDetailResponse]:
        """Get detailed meeting information with optional includes"""
        
        include_dict = {
            'organizer': True,
            'participants': True
        }
        
        if include_transcripts:
            include_dict['transcripts'] = True
            
        if include_summaries:
            include_dict['summaries'] = True
            
        if include_action_items:
            include_dict['actionItems'] = {'include': {'assignee': True}}
        
        meeting = await self.db.meeting.find_unique(
            where={'id': meeting_id},
            include=include_dict
        )
        
        if not meeting:
            return None
            
        return MeetingDetailResponse.from_orm(meeting)

    async def list_meetings(
        self,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None,
        organizer_email: Optional[str] = None
    ) -> List[MeetingResponse]:
        """List meetings with optional filtering"""
        
        where_clause = {}
        
        if status:
            where_clause['status'] = status
            
        if organizer_email:
            where_clause['organizer'] = {'email': organizer_email}
        
        meetings = await self.db.meeting.find_many(
            where=where_clause,
            include={
                'organizer': True,
                'participants': True
            },
            skip=skip,
            take=limit,
            order_by={'createdAt': 'desc'}
        )
        
        return [MeetingResponse.from_orm(meeting) for meeting in meetings]

    async def update_meeting(
        self,
        meeting_id: str,
        meeting_data: UpdateMeetingRequest
    ) -> Optional[MeetingResponse]:
        """Update meeting information"""
        
        # Check if meeting exists
        existing_meeting = await self.db.meeting.find_unique(
            where={'id': meeting_id}
        )
        
        if not existing_meeting:
            return None
        
        # Prepare update data
        update_data = {}
        if meeting_data.title is not None:
            update_data['title'] = meeting_data.title
        if meeting_data.description is not None:
            update_data['description'] = meeting_data.description
        if meeting_data.scheduled_at is not None:
            update_data['scheduledAt'] = meeting_data.scheduled_at
        if meeting_data.meeting_url is not None:
            update_data['meetingUrl'] = meeting_data.meeting_url
        if meeting_data.status is not None:
            update_data['status'] = meeting_data.status
            
        updated_meeting = await self.db.meeting.update(
            where={'id': meeting_id},
            data=update_data,
            include={
                'organizer': True,
                'participants': True
            }
        )
        
        return MeetingResponse.from_orm(updated_meeting)

    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting"""
        try:
            await self.db.meeting.delete(where={'id': meeting_id})
            return True
        except Exception:
            return False

    async def start_meeting(self, meeting_id: str) -> Optional[MeetingResponse]:
        """Start a meeting (update status and started_at time)"""
        
        meeting = await self.db.meeting.update(
            where={'id': meeting_id},
            data={
                'status': MeetingStatus.IN_PROGRESS,
                'startedAt': datetime.utcnow()
            },
            include={
                'organizer': True,
                'participants': True
            }
        )
        
        return MeetingResponse.from_orm(meeting) if meeting else None

    async def end_meeting(self, meeting_id: str) -> Optional[MeetingResponse]:
        """End a meeting (update status and ended_at time)"""
        
        meeting = await self.db.meeting.update(
            where={'id': meeting_id},
            data={
                'status': MeetingStatus.COMPLETED,
                'endedAt': datetime.utcnow()
            },
            include={
                'organizer': True,
                'participants': True
            }
        )
        
        return MeetingResponse.from_orm(meeting) if meeting else None

    async def add_participant(
        self,
        meeting_id: str,
        participant_data: AddParticipantRequest
    ) -> Optional[MeetingParticipantResponse]:
        """Add a participant to the meeting"""
        
        # Check if meeting exists
        meeting = await self.db.meeting.find_unique(where={'id': meeting_id})
        if not meeting:
            return None
        
        # Add participant
        participant = await self.db.meetingparticipant.create(
            data={
                'meetingId': meeting_id,
                'name': participant_data.name,
                'email': participant_data.email,
                'joinedAt': datetime.utcnow()
            }
        )
        
        return MeetingParticipantResponse.from_orm(participant)

    async def get_participants(self, meeting_id: str) -> List[MeetingParticipantResponse]:
        """Get all participants of a meeting"""
        
        participants = await self.db.meetingparticipant.find_many(
            where={'meetingId': meeting_id},
            order_by={'joinedAt': 'asc'}
        )
        
        return [MeetingParticipantResponse.from_orm(p) for p in participants]

    async def update_participant_status(
        self,
        participant_id: str,
        joined_at: Optional[datetime] = None,
        left_at: Optional[datetime] = None
    ) -> Optional[MeetingParticipantResponse]:
        """Update participant join/leave status"""
        
        update_data = {}
        if joined_at is not None:
            update_data['joinedAt'] = joined_at
        if left_at is not None:
            update_data['leftAt'] = left_at
            
        try:
            participant = await self.db.meetingparticipant.update(
                where={'id': participant_id},
                data=update_data
            )
            return MeetingParticipantResponse.from_orm(participant)
        except Exception:
            return None