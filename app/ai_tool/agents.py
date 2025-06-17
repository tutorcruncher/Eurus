import json
from dotenv import load_dotenv
from pydantic_ai import Agent
from app.ai_tool.system_prompts import (
    base_system_prompt,
    summary_system_prompt,
    tutor_feedback_system_prompt,
    student_feedback_system_prompt,
    lesson_plan_system_prompt,
    lesson_sequence_system_prompt
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
        response = await self.get_agent().run(transcript.to_concatonated_transcript())
        return response.output


class TutorFeedbackAgent(BaseAgent):
    system_prompt: str = tutor_feedback_system_prompt
    name: str = 'Tutor Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the tutor'
    )

    async def provide_feedback(self, transcript: Transcript, user_id: str):
        response = await self.get_agent().run(transcript.get_user_transcript(user_id))
        return json.loads(response.output)
    
    async def provide_feedback_with_str(self, transcript: str):
        response = await self.get_agent().run(transcript)
        return json.loads(response.output)


class StudentFeedbackAgent(BaseAgent):
    system_prompt: str = student_feedback_system_prompt
    name: str = 'Student Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the student'
    )

    async def provide_feedback(self, transcript: Transcript, user_id: str):
        response = await self.get_agent().run(transcript.get_user_transcript(user_id))
        return json.loads(response.output)

    async def provide_feedback_with_str(self, transcript: str):
        response = await self.get_agent().run(transcript)
        return json.loads(response.output)

class LessonPlanAgent(BaseAgent):
    system_prompt: str = lesson_plan_system_prompt
    name: str = 'Lesson Planning Agent'
    description: str = 'A helpful assistant that creates lesson plans'

    async def create_lesson_plan(self, lesson_info: dict):
        response = await self.get_agent().run(user_prompt=lesson_info.pop('plan'))
        return response.output
    

class LessonSequenceAgent(BaseAgent):
    system_prompt: str = lesson_sequence_system_prompt
    name: str = 'Lesson Sequence Agent'
    description: str = 'A helpful assistant that creates lesson sequences'

    async def create_lesson_sequence(self, lesson_info: dict):
        response = await self.get_agent().run(user_prompt=lesson_info.pop('sequence'))
        return json.loads(response.output)