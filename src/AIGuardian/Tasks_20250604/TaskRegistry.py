from a2a.types import (
    TaskState,
)
import json

class TaskRegistry():
    _registry = {}

    @classmethod
    def register(cls, task_name):
        def decorator(subclass):
            cls._registry[task_name] = subclass
            return subclass
        return decorator
    
    @classmethod
    def get_task(cls, task_name):
        """
        Get the Task class based on the Task name.
        """
        if task_name not in cls._registry:
            raise ValueError(f"Task '{task_name}' is not registered.")
        return cls._registry[task_name]

    @classmethod
    def build_from_json(cls, task_json, db_engine=None):
        """
        Build a Task from a JSON object.
        """
        task_name = task_json.get("task_name")
        if task_name not in cls._registry:
            raise ValueError(f"Task '{task_name}' is not registered.")
        task_obj = cls._registry[task_name]()
        task_obj.task_id = task_json.get("task_id")
        task_obj.task_name = task_json.get("task_name")
        # task_obj.task_version = task_json.get("task_version")
        task_obj.group_task_id = task_json.get("group_task_id")
        task_obj.sequence = task_json.get("sequence_number")
        task_obj.input_params = task_json.get("input_artifacts")
        task_obj.input_params = {} if task_obj.input_params is None else json.loads(task_obj.input_params)
        task_obj.db_engine = db_engine
        task_obj.task_state = TaskState.submitted if task_json.get("insert_dt", None) else None

        return task_obj