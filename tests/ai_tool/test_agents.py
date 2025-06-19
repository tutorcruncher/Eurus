from types import SimpleNamespace
import sys

import pytest

from app.ai_tool import agents as agent_module
from app.ai_tool.output_formats import LessonChaptersOutput, SummaryOutput
from app.models.transcript import Transcript


@pytest.fixture(autouse=True)
def _stub_agent(monkeypatch):
    """Replace ``pydantic_ai.Agent`` with a lightweight stub that records the call and returns predictable outputs."""

    calls = {}

    class DummyAgent:
        def __init__(self, name, description, model, system_prompt, output_type):
            # Save construction args for later assertions if needed.
            self.kwargs = {
                'name': name,
                'description': description,
                'model': model,
                'system_prompt': system_prompt,
                'output_type': output_type,
            }

        async def run(
            self, *args, **kwargs
        ):  # pragma: no cover – exercised asynchronously
            calls['run_called'] = True
            output_type = self.kwargs['output_type']
            # Produce minimal valid output for each type.
            if output_type is LessonChaptersOutput:
                output = LessonChaptersOutput(
                    chapters=[
                        {
                            'start_time': '0',
                            'end_time': '1',
                            'description': 'Intro',
                        }
                    ]
                )
            elif output_type is SummaryOutput:
                output = SummaryOutput(
                    key_points='kp',
                    short_summary='short' * 15,
                    long_summary='long' * 300,
                    recommended_focus='focus' * 15,
                )
            else:
                output = SimpleNamespace()
            return SimpleNamespace(output=output)

    monkeypatch.setattr(agent_module, 'Agent', DummyAgent, raising=False)
    monkeypatch.setitem(sys.modules, 'pydantic_ai', SimpleNamespace(Agent=DummyAgent))

    yield calls


def _sample_transcript():
    return Transcript(
        lesson_id='L1',
        transcription=[
            {
                'start_time': 0.0,
                'end_time': 1.0,
                'user': {'id': 1, 'name': 'A'},
                'breakout_id': 'main',
                'text': 'Hi',
            }
        ],
    )


@pytest.mark.asyncio
async def test_chapter_agent_breakdown(_stub_agent):
    chapters = await agent_module.ChapterAgent().break_down_lesson(_sample_transcript())
    assert chapters[0].description == 'Intro'
    assert _stub_agent.get('run_called') is True


@pytest.mark.asyncio
async def test_summary_agent(_stub_agent):
    summary = await agent_module.SummaryAgent().summarize_lesson(_sample_transcript())
    assert summary.key_points == 'kp'
    assert len(summary.long_summary) > 1000
