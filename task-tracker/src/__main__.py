#! /usr/bin/env python

from enum import Flag, auto
import argparse
from os.path import exists
from os import getenv, stat

from taskorganizer import TaskOrganizer, TaskStatus

FILEPATH = getenv("TASKS_PATH")


class TaskAction(Flag):
    list = auto()
    add = auto()
    update = auto()
    delete = auto()
    mark_in_progress = auto()
    mark_done = auto()
    mark_cancelled = auto()


def list_tasks(tko: TaskOrganizer, args: list[str]) -> None:
    if len(args) > 1:
        print("""\
list takes no argument or
        - done
        - in-progress
        - comitted
        - cancelled
        """)

    if len(args) == 0:
        for k, t in tko:
            print(f"## id: {k}", t)
    else:
        list_in_status = {
            "done": lambda: tko.get_in_status(TaskStatus.done),
            "in-progress": lambda: tko.get_in_status(TaskStatus.in_progress),
            "committed": lambda: tko.get_in_status(TaskStatus.committed),
            "cancelled": lambda: tko.get_in_status(TaskStatus.cancelled),
        }
        temp_list = list_in_status.get(args[0])
        if not temp_list:
            raise KeyError("The given Status does not exists: ", args[0])
        for k, t in temp_list().items():
            print(f"## id: {k}", t)


def add_tasks(tko: TaskOrganizer, args: list[str]) -> None:
    tmp_id = tko.add(*args)
    print(f"Task created with the id {tmp_id}", tko[tmp_id])


def update_tasks(tko: TaskOrganizer, args: list[str]) -> None:
    if len(args) < 3 or not args[0].isnumeric():
        print("""\
update needs an id and accepts title and notes as parameter
    example:
            task-cli update 0 title "new title" notes "new notes" status [done|in-progress|comitted|cancelled]
              """)
        return

    tmp_title: str | None = None
    tmp_notes: str | None = None
    tmp_status: str | None = None

    _argument_unkown: bool = False
    for i in range(1, len(args), 2):
        match args[i]:
            case "title":
                tmp_title = args[i + 1]
            case "notes":
                tmp_notes = args[i + 1]
            case "status":
                tmp_status = args[i + 1]
            case _:
                _argument_unkown = True

        if _argument_unkown:
            print(f"Argument not known: {args[i]}")
            return

    tko.update(id=int(args[0]), title=tmp_title, notes=tmp_notes, status=tmp_status)


def delete_tasks(tko: TaskOrganizer, args: list[str]) -> None:
    tko.delete(int(args[0]))


def mark_in_progress_tasks(tko: TaskOrganizer, args: list[str]) -> None:
    tko.update(id=int(args[0]), status="in_progress")


def mark_done_tasks(tko: TaskOrganizer, args: list[str]) -> None:
    tko.update(id=int(args[0]), status="done")


def mark_cancelled_tasks(tko: TaskOrganizer, args: list[str]) -> None:
    tko.update(id=int(args[0]), status="cancelled")


def save_tasks(tko: TaskOrganizer, filepath: str) -> None:
    with open(filepath, "w") as file:
        file.write(tko.dumps())


def init_tasks(tko: TaskOrganizer, filepath: str) -> None:
    if exists(filepath) and stat(filepath).st_size != 0:
        with open(filepath, "r") as file:
            tko.loads(file.read())


def main(flags: int, args: list[str]) -> None:
    if not FILEPATH:
        print("Please set path to file as TASKS_PATH variable")
        return

    action = {
        TaskAction.list.value: list_tasks,
        TaskAction.add.value: add_tasks,
        TaskAction.update.value: update_tasks,
        TaskAction.delete.value: delete_tasks,
        TaskAction.mark_in_progress.value: mark_in_progress_tasks,
        TaskAction.mark_done.value: mark_done_tasks,
        TaskAction.mark_cancelled.value: mark_cancelled_tasks,
    }

    tko = TaskOrganizer()

    # INFO: Initialize System
    init_tasks(tko, FILEPATH)

    if do_action := action.get(flags):
        do_action(tko, args)

    # INFO: Write Tasks to file
    save_tasks(tko, FILEPATH)


if __name__ == "__main__":
    flags: int = 0

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="actions")

    subparsers.add_parser("list", help="list Task").add_argument("args", nargs="*")
    subparsers.add_parser("add", help="add new Task").add_argument("args", nargs="*")
    subparsers.add_parser("update", help="update a Task").add_argument(
        "args", nargs="*"
    )
    subparsers.add_parser("delete", help="delete a Task").add_argument(
        "args", nargs="*"
    )
    subparsers.add_parser(
        "mark-in-progress", help="Set the status of a Task to in-progress"
    ).add_argument("args", nargs="*")
    subparsers.add_parser(
        "mark-done", help="Set the status of a Task to mark_done"
    ).add_argument("args", nargs="*")
    subparsers.add_parser(
        "mark-cancelled", help="Set the status of the Task to mark_cancelled"
    ).add_argument("args", nargs="*")

    args = parser.parse_args()

    if action := args.actions:
        # NOTE: i was not able to find a better way to return the correct string
        # --> mark-done is saved as "mark-done" but python does not allow dashes in names
        main(TaskAction[str(action).replace(r"-", r"_", 2)].value, args.args)

    else:
        print(parser.print_help())
