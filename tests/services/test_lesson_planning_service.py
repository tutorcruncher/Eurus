import pytest


# Skip the whole module if the real dependency is not available.
pytest.importorskip('pydantic_ai')


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_lesson_plan_service(monkeypatch):
    """LessonPlanService should delegate to its underlying agent."""

    from app.services.lesson_planning import LessonPlanService

    expected_output = {'plan': 'my lesson'}

    class DummyAgent:
        def create_lesson_plan(self, info):
            # Assert that the service passes the same dictionary down.
            assert info == {'topic': 'math'}
            return expected_output

    # Patch the agent class *before* service instantiation.
    monkeypatch.setattr(
        'app.services.lesson_planning.LessonPlanAgent', DummyAgent, raising=True
    )

    service = LessonPlanService()
    result = service.create_lesson_plan({'topic': 'math'})
    assert result == expected_output


def test_lesson_sequence_service(monkeypatch):
    """LessonSequenceService should delegate to its underlying agent."""

    from app.services.lesson_planning import LessonSequenceService

    expected_output = ['lesson-1', 'lesson-2']

    class DummyAgent:
        def create_lesson_sequence(self, info):
            assert info == {'sequence': 'numbers'}
            return expected_output

    monkeypatch.setattr(
        'app.services.lesson_planning.LessonSequenceAgent', DummyAgent, raising=True
    )

    service = LessonSequenceService()
    result = service.create_lesson_sequence({'sequence': 'numbers'})
    assert result == expected_output
