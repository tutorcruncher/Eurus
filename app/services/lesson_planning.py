from app.ai_tool.agents import LessonPlanAgent, LessonSequenceAgent


class LessonPlanService:
    def __init__(self):
        self.agent = LessonPlanAgent()

    def create_lesson_plan(self, info: dict):
        lesson_plan = self.agent.create_lesson_plan(info)
        return lesson_plan
    
class LessonSequenceService:
    def __init__(self):
        self.agent = LessonSequenceAgent()

    def create_lesson_sequence(self, info: dict):
        from devtools import debug
        debug(info)
        lesson_sequence = self.agent.create_lesson_sequence(info)
        return lesson_sequence
