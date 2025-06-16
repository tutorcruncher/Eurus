from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio
from pydantic_ai.messages import ModelMessagesTypeAdapter

from settings import Settings
from app.models.transcript import Transcript

settings = Settings()

# Load environment variables
load_dotenv()

system_prompt = """
Beep boop, I'm a chat agent.
"""


class BaseAgent:
    """Chat agent using pydantic-ai"""

    system_prompt: str = system_prompt
    model_name: str = settings.AI_MODEL
    name: str = 'The agent'
    description: str = 'A helpful chat assistant'

    def get_agent(self):
        return Agent(
            name=self.name,
            description=self.description,
            model=self.model_name,
            system_prompt=self.system_prompt,
        )


summary_system_prompt = """
You are a helpful assistant that summarizes lessons. You are making a summary of the lesson transcript that is being provided. Be aware that the transcript may have some issues with the order of text but should be 99% accurate.
Focus on what happened in the lesson, including the main points and the key takeaways.

The summary should be in the following format:

<summary>
{summary_paragrah_1}
{summary_paragrah_2}
{summary_paragrah_3}
{summary_paragrah_4}
{summary_paragrah_5}
</summary>

The summary should be 3 - 6 paragraphs long.
"""


class SummaryAgent(BaseAgent):
    system_prompt: str = summary_system_prompt
    name: str = 'Summary Agent'
    description: str = 'A helpful assistant that summarizes lessons'

    def summarize_lesson(self, transcript: Transcript):
        return self.get_agent().run(transcript.to_concatonated_transcript())


tutor_feedback_system_prompt = """
You are a tutoring coach. You are given a lesson transcript and you are providing feedback to the tutor on the lesson. Give feedback on the following:
- What the tutor did well
- What the tutor could improve on
- What the tutor could do differently
- What the tutor could do better
- What the tutor could do to improve the lesson
- What the tutor could do to improve the student's understanding
"""


class TutorFeedbackAgent(BaseAgent):
    system_prompt: str = tutor_feedback_system_prompt
    name: str = 'Tutor Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the tutor'
    )

    def provide_feedback(self, transcript: Transcript, user_id: str):
        return self.get_agent().run(transcript.get_user_transcript(user_id))


student_feedback_system_prompt = """
You are a tutor. You are given a lesson transcript and you are providing feedback to the student on their performance in the lesson.
Give feedback on the following:
- What the student did well
- What the student could improve on
- What the student could do differently
- What the student could do better
- What the student could do to improve the lesson
- What topics are good for the student to focus on & where to go next
"""


class StudentFeedbackAgent(BaseAgent):
    system_prompt: str = student_feedback_system_prompt
    name: str = 'Student Feedback Agent'
    description: str = (
        'A helpful assistant that provides feedback on lessons to the student'
    )

    def provide_feedback(self, transcript: Transcript, user_id: str):
        return self.get_agent().run(transcript.get_user_transcript(user_id))


# Prompts should probably be in a separate file
# Maybe feedback should be done in the same call or include both transcripts in the call
