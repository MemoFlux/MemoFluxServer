from abc import ABC, abstractmethod

from baml_py import Image

from src.schedules.schemas import Schedule

class ScheduleInterface(ABC):
    @abstractmethod
    async def gen_schedule_from_text(self, text: str) -> Schedule:
        pass
    
    @abstractmethod
    async def gen_schedule_from_image(self, image: Image) -> Schedule:
        pass