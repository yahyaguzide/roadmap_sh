"""
A task is a simple named tuple
"""

# This is Quaktastic
# >O
# _\)>
from typing import NamedTuple
from enum import Enum, auto
from datetime import datetime


class TaskStatus(Enum):
    committed = auto()
    in_progress = auto()
    done = auto()
    cancelled = auto()


class Task(NamedTuple):
    title: str
    notes: str
    status: TaskStatus
    creation_date: datetime
    update_date: datetime

    def __str__(self) -> str:
        return f"""
        ### {self.title} ###
        {self.notes}
        status: {self.status.name}
        creation: {self.creation_date.strftime("%d/%m/%Y")}
        last updated: {self.update_date.strftime("%d/%m/%Y")}"""
