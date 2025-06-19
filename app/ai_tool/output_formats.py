from pydantic import BaseModel, Field


class BasicOutput(BaseModel):
    text_response: str


class FeedbackOutput(BaseModel):
    strengths: list[str] = Field(
        description="The strengths of the user's lesson",
        min_items=3,
        max_items=10,
        default=[],
    )
    improvements: list[str] = Field(
        description="The improvements to the user's lesson",
        min_items=3,
        max_items=10,
        default=[],
    )


class ChapterOutput(BaseModel):
    start_time: str = Field(description='The start time of the lesson')
    end_time: str = Field(description='The end time of the lesson')
    description: str = Field(description='The description of the chapter')


class LessonChaptersOutput(BaseModel):
    chapters: list[ChapterOutput] = Field(description='The chapters of the lesson')


class LessonPlanOutput(BaseModel):
    lesson_plan: str = Field(
        description='The lesson plan for the lesson', min_length=1000, max_length=10000
    )


class SummaryOutput(BaseModel):
    key_points: str = Field(
        description='The key points of the lesson in unformatted markdown', default=''
    )
    short_summary: str = Field(
        description='The short summary of the lesson in unformatted markdown',
        default='',
        # min_length=50,
        # max_length=250,
    )
    long_summary: str = Field(
        description='The long summary of the lesson in unformatted markdown',
        default='',
        # min_length=1000,
        # max_length=10000,
    )
    recommended_focus: str = Field(
        description='The recommended focus of the lesson in unformatted markdown',
        default='',
        # min_length=50,
        # max_length=250,
    )


class LessonSequenceOutput(BaseModel):
    lesson_sequence: list[LessonPlanOutput] = Field(
        description='The collection of lesson plans for the lesson sequence'
    )
