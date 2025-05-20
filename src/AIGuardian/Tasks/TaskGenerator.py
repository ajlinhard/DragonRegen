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
    
    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return {
            "output_type": GenAIUtils.valid_output_type("taskList"),
            "output_struct": [],
        }
    
    # region task Methods
    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the task based on the user input.
        """
        # This method should be overridden in subclasses to provide specific prompts
        raise Exception(f"This function should not be called for {__class__.__name__} class types, because they do not call AI!")
    
    def get_messages(self):
        """
        Get the messages for the task.
        """
        # This method should be overridden in subclasses to provide specific messages
        raise Exception("This function should not be called for {__class__.__name__} class types, because they do not call AI!")
    
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the task.
        """
        # This method should be overridden in subclasses to provide specific validation
         # Reserved parameters for the tasks
            # ai_tools -> used for feeding to the AI to potentially use.
            # rag_objects -> used for potentially pulling or pushing to the AI.
        return True
    
    def hygiene_output(self, text_response):
        """
        Clean the output of the task.
        """
        # This method should be overridden in subclasses to provide specific cleaning
        return text_response
    
    def validate_output(self, text_response):
        """
        Validate the output of the task.
        """
        # This method should be overridden in subclasses to provide specific validation
        self.text_response = text_response
        return True
    
    @Task.record_step(TaskState.completed)
    def complete_task(self):
        """
        Complete the task based of the values from the AI gnerated response. Fill in the output_params for the task.
        """
        # This method should be overridden in subclasses to provide specific completion tasks
        self.is_completed = True
    
    @Task.record_step(TaskState.input_required)
    def wait_on_dependency(self, timeout=180):
        """
        Wait for the Task to complete before proceeding.
        """
        super().wait_on_dependency(timeout=timeout)

    def get_tools(self):
        """
        Get the tools for this task class or utility classes for the AI to consider using.
        """
        # This method should be overridden in subclasses to provide specific tools
        return []

    def geneterate_tasks(self):
        """
        Generate tasks based on the schema.
        """
        self.child_task = [] if self.child_task is None else self.child_task
        return self.child_task

    def run(self, user_prompt=None):
        """
        Run the code to generate schema refinement tasks.
        """
        if self._task_state != TaskState.working:
            self.initialize()
        
        self.geneterate_tasks()

        self.wait_on_dependency()

        self.complete_task()
    # endregion task Methods
