import json
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskState,
)

from ..Tasks.Task import Task
from ..Tasks.TaskGenerator import TaskGenerator
from ..Tasks.ColumnRefiner import ColumnRefiner
from ..AIUtils import GenAIUtils


class SchemaRefiner(TaskGenerator):
    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_task=None):
        super().__init__(input_params, sequence_limit, verbose, parent_task)

    # region static variables
    @staticmethod
    def get_description():
        return """Create a set of sub-tasks to refine the schema with more details."""
    
    @staticmethod
    def get_task_type():
        return 'schema'
    
    @staticmethod
    def get_task_version():
        return '0.0.1'

    # endregion static variables
    
    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return {
            "output_type": GenAIUtils.valid_output_type("taskList"),
            "output_struct": [ColumnRefiner],
        }
    
    # region task Methods
    async def geneterate_tasks(self):
        """
        Generate tasks based on the schema.
        """
        self.child_task = [] if self.child_task is None else self.child_task
        for table_name, table_info in self.input_params.items():
            if isinstance(table_info, dict):
                # Generate tasks for each table and its fields
                task_parameters = {
                    "table_name": table_name,
                    "purpose": table_info["purpose"],
                    "fields": table_info["fields"]
                }
                task = ColumnRefiner(task_parameters)
                self.child_task.append(task)
        return self.child_task
    
    @Task.record_step(TaskState.completed)
    def complete_task(self):
        # Loop through the child tasks and rebuild the schema.
        d_tables = {}
        for task in self.child_task:
            if isinstance(task, ColumnRefiner):
                d_tables = {**d_tables, **task.output_params}
        self.output_params = d_tables
        return self.output_params

    async def run(self, user_prompt=None):
        """
        Run the code to generate schema refinement tasks.
        """
        await super().run(user_prompt)

    # region task Methods
