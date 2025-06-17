from app.ai_tool.agents import LessonPlanAgent


class LessonPlanService:
    def __init__(self):
        self.agent = LessonPlanAgent()

    def create_lesson_plan(self, info: dict):
        lesson_plan = self.agent.create_lesson_plan(info)
        return lesson_plan
