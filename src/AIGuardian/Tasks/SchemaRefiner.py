import json
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskState,
)

from src.AIGuardian.Tasks.Task import Task
from src.AIGuardian.Tasks.TaskGenerator import TaskGenerator
from src.AIGuardian.Tasks.ColumnRefiner import ColumnRefiner
from src.AIGuardian.AIUtils import GenAIUtils
from src.AIGuardian.Tasks.TaskRegistry import TaskRegistry

@TaskRegistry.register("SchemaRefiner")
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
    def geneterate_tasks(self):
        """
        Generate tasks based on the schema.
        """
        self.child_task = [] if self.child_task is None else self.child_task
        generated_tasks = []
        print(f"SchemaRefiner: {type(self.input_params)}")
        print(f"SchemaRefiner: {self.input_params}")
        for table_name, table_info in self.input_params.items():
            if isinstance(table_info, dict):
                # Generate tasks for each table and its fields
                print(f"SchemaRefiner: {table_info}")
                task_parameters = {
                    "table_name": table_name,
                    "purpose": table_info["purpose"],
                    "fields": table_info["fields"]
                }
                task = ColumnRefiner(task_parameters, parent_task=self)
                generated_tasks.append(task)
                self.child_task.append(task.task_id)
        return generated_tasks
    
    def complete_task(self):
        # Loop through the child tasks and rebuild the schema.
        d_tables = {}
        for task in self.child_task:
            if isinstance(task, ColumnRefiner):
                d_tables = {**d_tables, **task.output_params}
        self.output_params = d_tables

        d_tables = {}
        for key, val in self.child_task_output_artifacts.items():
            if isinstance(val, dict):
                d_tables = {**d_tables, **val}
            else:
                d_tables = {**d_tables, **json.loads(val)}
        
        self.output_params = d_tables
        return super().complete_task()

    # region task Methods
