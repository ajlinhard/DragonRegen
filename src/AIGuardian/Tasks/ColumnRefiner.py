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
from .TaskGenerator import TaskGenerator
from .DataColumnType import DataColumnType
from .DataColumnRefiner import DataColumnRefiner
from ..AIUtils.GenAIUtils import GenAIUtils

@TaskRegistry.register("ColumnRefiner")
class ColumnRefiner(TaskGenerator):
    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_task=None):
        super().__init__(input_params, sequence_limit, verbose, parent_task)
        # specific to this type of task
        self.data_column_refiner = []


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
    def geneterate_tasks(self):
        """
        Generate tasks based on the schema.
        """
        self.child_task = [] if self.child_task is None else self.child_task
        self.data_column_refiner = []
        table_name = self.input_params.get("table_name")
        table_purpose = self.input_params.get("purpose")
        for col_name, col_description in self.input_params['fields'].items():
            # Generate tasks for each table and its fields
            task_parameters = {
                "table_name": table_name,
                "purpose": table_purpose,
                "column_name": col_name,
                "description": col_description,
            }
            task_1 = DataColumnType(task_parameters, parent_task=self)
            task_1.submit_task()
            self.child_task.append(task_1.task_id)
            task_2 = DataColumnRefiner(task_parameters, parent_task=task_1)
            task_2.submit_task()
            self.child_task.append(task_2.task_id)
            self.data_column_refiner.append(task_2.task_id)
        return self.child_task
    
    @Task.record_step(TaskState.completed)
    def complete_task(self):
        # Loop through the child tasks and rebuild the schema.
        ls_fields = []
        for key, val in self.child_task_output_artifacts.items():
            if key in self.data_column_refiner:
                print(f" Adding Key: {key} to the list of fields")
                ls_fields.append(val)
        
        self.output_params = {self.input_params.get("table_name"):
                {"purpose": self.input_params.get("purpose"), "fields": ls_fields}}
        return super().complete_task()

    def run(self, user_prompt=None):
        """
        Run the code to generate schema refinement tasks.
        """
        super().run(user_prompt)

    # endregion task Methods
    