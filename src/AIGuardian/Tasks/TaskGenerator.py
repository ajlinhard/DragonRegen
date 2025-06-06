import json
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskState,
)
from .Task import Task
from .TaskRegistry import TaskRegistry
from ..AIUtils.GenAIUtils import GenAIUtils

@TaskRegistry.register("TaskGenerator")
class TaskGenerator(Task):
    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_task=None):
        super().__init__(input_params, sequence_limit, verbose, parent_task)
        # override the Task class variables
        self.function_order = [self.initialize, self.geneterate_tasks, self.complete_task]

    # region static variables
    @staticmethod
    def get_description():
        return """Create a set of sub-tasks to be run."""
    
    @staticmethod
    def get_task_type():
        return 'Generator'
    
    @staticmethod
    def get_task_version():
        return '0.0.1'

    @staticmethod
    def get_system_prompt():
        return None # This does not call the AI APIs, so None will indicate this for the system.
    
    # endregion static variables

    def complete_task(self):
        """
        Complete the task based of the values from the AI gnerated response. Fill in the output_params for the task.
        """
        # This method should be overridden in subclasses to provide specific completion tasks
        return super().complete_task()

    def geneterate_tasks(self):
        """
        Generate tasks based on the schema.
        """
        self.child_task = [] if self.child_task is None else self.child_task
        return self.child_task

    # endregion task Methods
