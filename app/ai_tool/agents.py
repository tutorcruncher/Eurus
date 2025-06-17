import json
from dotenv import load_dotenv
from pydantic_ai import Agent
from app.ai_tool.system_prompts import (
    base_system_prompt,
    summary_system_prompt,
    tutor_feedback_system_prompt,
    student_feedback_system_prompt,
    lesson_plan_system_prompt,
)

from app.utils.settings import Settings
from app.models.transcript import Transcript

settings = Settings()

# Load environment variables
load_dotenv()


class BaseAgent:
    """Chat agent using pydantic-ai"""

    system_prompt: str = base_system_prompt
    model_name: str
    name: str = 'The agent'
    description: str = 'A helpful chat assistant'

    def __init__(self):
        self.model_name = settings.ai_model

    def get_agent(self):
        return Agent(
            name=self.name,
            description=self.description,
            model=self.model_name,
            system_prompt=self.system_prompt,
        )


class SummaryAgent(BaseAgent):
    system_prompt: str = summary_system_prompt
    name: str = 'Summary Agent'
    description: str = 'A helpful assistant that summarizes lessons'

    async def summarize_lesson(self, transcript: Transcript):
        return await self.get_agent().run(transcript.to_concatonated_transcript())


class TutorFeedbackAgent(BaseAgent):
    system_prompt: str = tutor_feedback_system_prompt
    name: str = 'Tutor Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the tutor'
    )

    async def provide_feedback(self, transcript: Transcript, user_id: str):
        return await self.get_agent().run(transcript.get_user_transcript(user_id))


class StudentFeedbackAgent(BaseAgent):
    system_prompt: str = student_feedback_system_prompt
    name: str = 'Student Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the student'
    )

    async def provide_feedback(self, transcript: Transcript, user_id: str):
        return await self.get_agent().run(transcript.get_user_transcript(user_id))


class LessonPlanAgent(BaseAgent):
    system_prompt: str = lesson_plan_system_prompt
    name: str = 'Lesson Plan Agent'
    description: str = 'A helpful assistant that creates lesson plans'

    async def create_lesson_plan(self, lesson_info: dict):
        ree = await self.get_agent().run(user_prompt=lesson_info.pop('plan'))
        return json.loads(ree.output)
