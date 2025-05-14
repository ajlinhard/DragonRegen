import json
from ..Tasks.Task import Task
from ..Tasks.TaskGenerator import TaskGenerator
from ..Tasks.DataColumnType import DataColumnType
from ..Tasks.DataColumnRefiner import DataColumnRefiner
from ..AIUtils.GenAIUtils import GenAIUtils

class ColumnRefiner(TaskGenerator):
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
            task_1 = DataColumnType(task_parameters)
            self.child_task.append(task_1)
            task_2 = DataColumnRefiner(task_parameters, parent_task=task_1)
            self.child_task.append(task_2)
        return self.child_task
    
    @Task.record_step("COMPLETED")
    def complete_task(self):
        # Loop through the child tasks and rebuild the schema.
        ls_fields = []
        for task in self.child_task:
            if isinstance(task, DataColumnRefiner):
                ls_fields.append(task.output_params)
        self.output_params = {self.input_params.get("table_name"):
                {"purpose": self.input_params.get("purpose"), "fields": ls_fields}}
        return self.output_params

    async def run(self, user_prompt=None):
        """
        Run the code to generate schema refinement tasks.
        """
        await super().run(user_prompt)

    # endregion task Methods
    