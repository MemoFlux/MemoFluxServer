from pydantic import BaseModel

class Task(BaseModel):
    task_id: int
    start_time: str
    end_time: str
    people: list[str]
    theme: str
    core_tasks: list[str]
    position: list[str]
    tags: list[str]
    category: str
    suggested_actions: list[str]

class Schedule(BaseModel):
    id: str
    title: str
    text: str
    tasks: list[Task]