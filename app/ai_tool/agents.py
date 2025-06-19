import json
from dotenv import load_dotenv
from pydantic_ai import Agent
from app.ai_tool.output_formats import (
    BasicOutput,
    LessonChaptersOutput,
    LessonPlanOutput,
    LessonSequenceOutput,
    FeedbackOutput,
    SummaryOutput,
)
from app.ai_tool.system_prompts import (
    base_system_prompt,
    summary_system_prompt,
    tutor_feedback_system_prompt,
    student_feedback_system_prompt,
    lesson_plan_system_prompt,
    lesson_sequence_system_prompt,
    chapter_system_prompt,
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
    output_type = BasicOutput

    def __init__(self):
        self.model_name = settings.ai_model

    def get_agent(self):
        return Agent(
            name=self.name,
            description=self.description,
            model=self.model_name,
            system_prompt=self.system_prompt,
            output_type=self.output_type,
        )


class ChapterAgent(BaseAgent):
    system_prompt: str = chapter_system_prompt
    name: str = 'Chapter Agent'
    description: str = 'A helpful assistant that breaks down lessons into chapters'
    output_type = LessonChaptersOutput

    async def break_down_lesson(self, transcript: Transcript):
        response = await self.get_agent().run(json.dumps(transcript.transcription))
        return response.output.chapters


class SummaryAgent(BaseAgent):
    system_prompt: str = summary_system_prompt
    name: str = 'Summary Agent'
    description: str = 'A helpful assistant that summarizes lessons'
    output_type = SummaryOutput

    async def summarize_lesson(self, transcript: Transcript):
        response = await self.get_agent().run(transcript.to_concatonated_transcript())
        return response.output


class FeedbackAgent(BaseAgent):
    output_type = FeedbackOutput

    async def provide_feedback(self, transcript: Transcript, user_id: str):
        response = await self.get_agent().run(transcript.get_user_transcript(user_id))
        return json.loads(response.output)

    async def provide_feedback_with_str(self, transcript: str):
        response = await self.get_agent().run(transcript)
        output = response.output
        return output.strengths, output.improvements


class TutorFeedbackAgent(FeedbackAgent):
    name: str = 'Tutor Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the tutor'
    )

    def __init__(self, tutors_name: str):
        super().__init__()
        self.system_prompt = tutor_feedback_system_prompt(tutors_name)


class StudentFeedbackAgent(FeedbackAgent):
    name: str = 'Student Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the student'
    )

    def __init__(self, students_name: str):
        super().__init__()
        self.system_prompt = student_feedback_system_prompt(students_name)


class LessonPlanAgent(BaseAgent):
    system_prompt: str = lesson_plan_system_prompt
    name: str = 'Lesson Planning Agent'
    description: str = 'A helpful assistant that creates lesson plans'
    output_type = LessonPlanOutput

    async def create_lesson_plan(self, lesson_info: dict):
        response = await self.get_agent().run(user_prompt=lesson_info.pop('plan'))
        return response.output


class LessonSequenceAgent(BaseAgent):
    system_prompt: str = lesson_sequence_system_prompt
    name: str = 'Lesson Sequence Agent'
    description: str = 'A helpful assistant that creates lesson sequences'
    output_type = LessonSequenceOutput

    async def create_lesson_sequence(self, lesson_info: dict):
        response = await self.get_agent().run(user_prompt=lesson_info.pop('sequence'))
        return json.loads(response.output)
