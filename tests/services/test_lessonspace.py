import pytest
from unittest.mock import patch, AsyncMock, Mock
from datetime import datetime, timezone
from fastapi import HTTPException
from app.services.lessonspace import LessonspaceService
from app.schema.space import SpaceRequest, User, LeaderUser, UserSpace


@pytest.fixture
def lessonspace_service(settings):
    return LessonspaceService()


@pytest.fixture
def mock_user():
    return LeaderUser(user_id='test-user-123', name='Test User', is_leader=True)


@pytest.fixture
def mock_space_request():
    return SpaceRequest(
        lesson_id='test-lesson-123',
        tutors=[
            LeaderUser(user_id='tutor-1', name='Tutor One', is_leader=True),
            LeaderUser(user_id='tutor-2', name='Tutor Two', is_leader=False),
        ],
        students=[
            User(user_id='student-1', name='Student One'),
            User(user_id='student-2', name='Student Two'),
        ],
        not_before=datetime(2024, 3, 20, 10, 0, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_create_user_space_success(lessonspace_service, mock_user):
    mock_response = {
        'client_url': 'https://test.thelessonspace.com/space/test-123',
        'room_id': 'test-room-123',
    }

    with patch('httpx.AsyncClient') as mock_client:
        mock_response_obj = AsyncMock()
        mock_response_obj.json = Mock(return_value=mock_response)
        mock_response_obj.raise_for_status = Mock()
        mock_client.return_value.__aenter__.return_value.post.return_value = (
            mock_response_obj
        )

        user_space, room_id = await lessonspace_service._create_user_space(
            mock_client.return_value.__aenter__.return_value,
            'test-lesson-123',
            mock_user,
            'tutor',
            True,
        )

        assert user_space.user_id == mock_user.user_id
        assert user_space.name == mock_user.name
        assert user_space.role == 'tutor'
        assert user_space.space_url == mock_response['client_url']
        assert room_id == mock_response['room_id']
        assert user_space.leader is True


@pytest.mark.asyncio
async def test_get_or_create_space_success(lessonspace_service, mock_space_request):
    def user_space_factory(user, role, leader):
        return UserSpace(
            user_id=user.user_id,
            name=user.name,
            role=role,
            space_url=f'https://test.com/{user.user_id}',
            leader=leader,
        )

    async def mock_create_user_space(
        client, lesson_id, user, role, leader, not_before=None
    ):
        return user_space_factory(user, role, leader), 'test-room-123'

    with patch.object(
        lessonspace_service, '_create_user_space', side_effect=mock_create_user_space
    ):
        response = await lessonspace_service.get_or_create_space(mock_space_request)
        assert response.lesson_id == mock_space_request.lesson_id
        assert response.space_id == 'test-room-123'
        assert len(response.tutor_spaces) == 2
        assert len(response.student_spaces) == 2


@pytest.mark.asyncio
async def test_get_or_create_space_error(lessonspace_service, mock_space_request):
    async def raise_error(*args, **kwargs):
        raise Exception('API Error')

    with patch.object(
        lessonspace_service, '_create_user_space', side_effect=raise_error
    ):
        with pytest.raises(HTTPException) as exc_info:
            await lessonspace_service.get_or_create_space(mock_space_request)
        assert exc_info.value.status_code == 500
        assert 'Internal server error' in str(exc_info.value.detail)
