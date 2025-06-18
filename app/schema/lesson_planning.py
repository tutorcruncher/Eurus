from pydantic import BaseModel


# class LessonPlanResponse(BaseModel):
#     basic_information: str
#     learning_objectives: str
#     materials_and_resources: str
#     instructional_steps: str
#     assessment: str
#     reflection: str
#     suggestions_for_homework: str


class LessonPlanResponse(BaseModel):
    lesson_plan: str


class LessonSequenceResponse(BaseModel):
    lesson_plans: list[LessonPlanResponse]
