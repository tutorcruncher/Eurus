import httpx
from app.utils.settings import get_settings
from app.schema.space import SpaceRequest, SpaceResponse, UserSpace
import asyncio
from fastapi import HTTPException
from app.utils.dataclass import BaseRequest
from dataclasses import dataclass
from typing import Optional, Dict, Union
from app.utils.logging import logger
from sqlmodel import Session, select
from app.models.transcript import Space as SpaceDB, UserSpace as UserSpaceDB

settings = get_settings()


@dataclass
class LessonSpaceRequest(BaseRequest):
    id: Union[int, str]
    user: Dict[str, Union[str, bool]]
    transcribe: bool = True
    record_av: bool = True
    webhooks: Optional[Dict] = None
    timeouts: Optional[Dict] = None


class LessonspaceService:
    def __init__(self):
        self.api_key = settings.lessonspace_api_key
        self.base_url = settings.lessonspace_api_url
        self.headers = {'Authorization': f'Organisation {self.api_key}'}

    async def _create_user_space(
        self,
        client,
        lesson_id,
        user,
        role,
        leader: bool,
        not_before=None,
    ):
        request = LessonSpaceRequest(
            id=lesson_id,
            user={
                'id': user.user_id,
                'name': user.name,
                'role': role,
                'leader': leader,
            },
            webhooks={
                'transcription': {
                    'finish': f'{settings.base_url}/api/space/webhook/transcription/{lesson_id}'
                }
            },
        )

        if not_before:
            request.timeouts = {'not_before': not_before.isoformat()}

        resp = await client.post(
            f'{self.base_url}/spaces/launch/',
            headers=self.headers,
            json=request.to_dict(),
        )
        resp.raise_for_status()
        data = resp.json()
        return UserSpace(
            user_id=user.user_id,
            name=user.name,
            role=role,
            space_url=data['client_url'],
            leader=leader,
        ), data['room_id']

    async def get_or_create_space(
        self, request: SpaceRequest, db: Optional[Session] = None
    ) -> SpaceResponse:
        try:
            async with httpx.AsyncClient() as client:
                tasks = []
                for tutor in request.tutors:
                    tasks.append(
                        self._create_user_space(
                            client,
                            request.lesson_id,
                            tutor,
                            'tutor',
                            tutor.is_leader,
                            request.not_before,
                        )
                    )
                for student in request.students:
                    tasks.append(
                        self._create_user_space(
                            client,
                            request.lesson_id,
                            student,
                            'student',
                            False,
                            request.not_before,
                        )
                    )
                results = await asyncio.gather(*tasks)
                user_spaces, room_ids = zip(*results)
                tutor_spaces = [us for us in user_spaces if us.role == 'tutor']
                student_spaces = [us for us in user_spaces if us.role == 'student']
                space_id = room_ids[0] if room_ids else None
                space_response = SpaceResponse(
                    space_id=space_id,
                    lesson_id=request.lesson_id,
                    tutor_spaces=tutor_spaces,
                    student_spaces=student_spaces,
                )

                logger.info(
                    '[LessonSpaceService] created new space',
                    lesson_id=request.lesson_id,
                    space_id=space_id,
                    tutor_count=len(tutor_spaces),
                    student_count=len(student_spaces),
                    not_before=request.not_before.isoformat()
                    if request.not_before
                    else None,
                )

                # Persist to database if session provided
                if db is not None:
                    # Ensure a Space record exists for this lesson
                    space_db = db.exec(
                        select(SpaceDB).where(SpaceDB.lesson_id == request.lesson_id)
                    ).first()
                    if space_db is None:
                        space_db = SpaceDB(lesson_id=request.lesson_id)
                        db.add(space_db)
                        db.commit()
                        db.refresh(space_db)

                    # Create UserSpace records
                    for us in user_spaces:
                        existing_us = db.exec(
                            select(UserSpaceDB)
                            .where(UserSpaceDB.space_id == space_db.id)
                            .where(UserSpaceDB.user_id == us.user_id)
                        ).first()
                        if existing_us is None:
                            db.add(
                                UserSpaceDB(
                                    user_id=us.user_id,
                                    role=us.role,
                                    leader=us.leader,
                                    space_id=space_db.id,
                                )
                            )
                    db.commit()

                return space_response
        except Exception as e:
            logger.error(
                '[LessonSpaceService] error in get_or_create_space',
                lesson_id=request.lesson_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=500, detail='Internal server error: ' + str(e)
            )
