from src.baml_client.types import Task as BamlTask, Schedule as BamlSchedule

class Task(BamlTask):
    id: int

class Schedule(BamlSchedule):
    id: str