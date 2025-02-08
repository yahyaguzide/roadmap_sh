"""
Simple TaskOrganizer which creates updates and deletes Task objects
"""

from dataclasses import dataclass, field
from typing import TypeVar

# from enum import Enum, auto
from datetime import datetime
from json import dumps as json_dumps
from json import loads as json_loads

from task import Task, TaskStatus

T = TypeVar("T")


class TaskingError(Exception):
    pass


@dataclass(slots=True, kw_only=True)
class TaskOrganizer:
    _tasks: dict[int, Task] = field(init=False, default_factory=dict)

    def get_by_id(self, id: int, default: T = None) -> Task | T:
        """
        Returns the Task with the specified ID or as default None or Type T if not found.

        params:
            id: str

        returns: Task | None
        """

        return self._tasks.get(id, default)

    def add(self, title: str, notes: str = "") -> int:
        """
        Create and add a Task to the list

        params:
            title: str
            notes: str

        returns: str
        """

        # find a free id
        id: int = 0
        for id in range(0, len(self._tasks) + 1):
            if id not in self._tasks:
                break

        dt_now = datetime.now().replace(microsecond=0)
        self._tasks[id] = Task(
            title=title,
            notes=notes,
            status=TaskStatus.committed,
            creation_date=dt_now,
            update_date=dt_now,
        )
        return id

    def update(
        self,
        id: int,
        title: str | None = None,
        notes: str | None = None,
        status: str | None = None,
    ) -> int | None:
        """
        Update a Task.
        This will delete the initial Task and create a new one
        with the updated values.
        If Task is found and updated returns the uuid of the Task

        params:
            id (str): The id of the Task
            title (str | None): New title of the Task
            notes (str | None): New notes of the Task
            status (str | None): New status of the Task

        returns: returns the id (str) if successfull
        """

        if id not in self._tasks:
            raise TaskingError("Not a valid ID: ", id)

        if status:
            try:
                TaskStatus[status]
            except KeyError:
                raise TaskingError("Not a proper Status: ", status)

        tmp_title = title if title else self._tasks[id].title
        tmp_notes = notes if notes else self._tasks[id].notes
        tmp_status = TaskStatus[status] if status else self._tasks[id].status
        tmp_update_date = (
            datetime.now().replace(microsecond=0)
            if title or notes or status
            else self._tasks[id].update_date
        )

        self._tasks[id] = Task(
            title=tmp_title,
            notes=tmp_notes,
            status=tmp_status,
            creation_date=self._tasks[id].creation_date,
            update_date=tmp_update_date,
        )

        return id

    def delete(self, id: int) -> int:
        """
        Delete a Task from the list
        If Task is found and deleted returns the uuid of the Task
        or None if id does not exists

        params:
        returns: str | None
        """

        if id not in self._tasks:
            raise TaskingError("Not a valid ID: ", id)

        del self._tasks[id]

        return id

    def get_in_status(self, status: TaskStatus) -> dict[int, Task]:
        """
        Returns a list of Tasks with the given status

        params:
            status: TaskStatus

        returns: list[Task]
        """

        return {k: v for k, v in self._tasks.items() if v.status == status}

    def _task_to_list(self, t: Task) -> list[str]:
        date_format = "%Y-%m-%d %H:%M:%S"
        return [
            t.title,
            t.notes,
            t.status.name,
            t.creation_date.strftime(date_format),
            t.update_date.strftime(date_format),
        ]

    def _list_to_task(self, tl: list[str]) -> Task:
        date_format = "%Y-%m-%d %H:%M:%S"
        return Task(
            tl[0],
            tl[1],
            getattr(TaskStatus, tl[2], TaskStatus.committed),
            datetime.strptime(tl[3], date_format),
            datetime.strptime(tl[4], date_format),
        )

    def dumps(self) -> str:
        """
        Returns a json in str

        params:

        returns: str
        """

        return json_dumps(
            {k: self._task_to_list(t) for k, t in self._tasks.items()}, default=str
        )

    def loads(self, data: str) -> None:
        """
        Loads a string formatted in json as dict and writes it to _tasks

        params:
            data: str

        returns: None
        """

        for k, t in json_loads(data).items():
            self._tasks[int(k)] = self._list_to_task(t)

    def __getitem__(self, key: int):
        return self._tasks[key]

    def __iter__(self):
        return iter(self._tasks.items())

    def __len__(self):
        return len(self._tasks)
