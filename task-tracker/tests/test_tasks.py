from _pytest.assertion import AssertionState
import pytest

from src.taskorganizer import TaskOrganizer, TaskStatus
from task import Task


class Test_add_update_delete:
    @pytest.fixture(scope="function")
    def get_initialized_taskorganizer(self):
        taskorg = TaskOrganizer()

        test_title = "test title"
        test_notes = "test notes"

        task_id = taskorg.add(test_title, test_notes)

        return (task_id, taskorg)

    def test_add(self):
        taskorg = TaskOrganizer()

        test_title = "test title"
        test_notes = "test notes"

        try:
            task_id = taskorg.add(test_title, test_notes)
        except Exception as e:
            assert False, f"The following Exception occured: {e}"

        task: Task | None
        assert (
            task := taskorg._tasks.get(task_id)
        ), "Task was not creates correcty, id not found in dict"

        assert task.title == test_title, "Incorrect title for Task"
        assert task.notes == test_notes, "Incorrect notes for Task"

    def test_update(self, get_initialized_taskorganizer):
        task_id, taskorg = get_initialized_taskorganizer

        new_test_title = "new test title"

        new_task_id = taskorg.update(id=task_id, title=new_test_title)

        assert not taskorg.get(task_id), "Old Taks not deleted"
        assert taskorg.get(new_task_id), "New Task not added"
        assert (
            taskorg.get(new_task_id).title == new_test_title
        ), "new title is not correct"

    def test_delete(self, get_initialized_taskorganizer):
        task_id, taskorg = get_initialized_taskorganizer

        taskorg.delete(task_id)
        assert not taskorg._tasks, "task dict not empty, _tasks should have been empty"

    def test_get_tasks_in_status(self, get_initialized_taskorganizer):
        task_id, taskorg = get_initialized_taskorganizer

        taskorg.add("test title 2", "test notes 2")
        taskorg.add("test title 3", "test notes 3")

        taskorg.update(task_id, status=TaskStatus.in_progress)

        committed_tasks = taskorg.get_task_in_status(status=TaskStatus.in_progress)

        assert isinstance(committed_tasks, list), "Incorrect type returned"

        for t in committed_tasks:
            if t.status != TaskStatus.committed:
                assert False, "Not committed task found in committed tasks"

        in_progress_tasks = taskorg.get_task_in_status(status=TaskStatus.committed)

        assert isinstance(in_progress_tasks, list), "Incorrect type returned"

        for t in in_progress_tasks:
            if t.status != TaskStatus.in_progress:
                assert False, "Not committed task found in in_progress tasks"

    def test_clone_task(self):
        pass

    def dumps(self):
        pass
