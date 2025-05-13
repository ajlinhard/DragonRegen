from abc import ABC, abstractmethod
import datetime
import json
from .Task import Task
from .TaskExceptions import ValidateAIResponseError
from ...DataCreator.SchemaGenerators.SchemaMSSQL import SchemaMSSQL
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine

@Task.register("TaskSayHello")
class TaskSayHello(Task):

    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_task=None):
        self.input_params = input_params
        super().__init__(input_params=input_params, sequence_limit=sequence_limit, verbose=verbose, parent_task=parent_task)
        self.model_parameters = {"model": "claude-3-haiku-20240307",
            "max_tokens": 200,
            "temperature": 0.1,
            "stop_sequences": ["</JSON_Template>"],
            "pref_model_type": "SIMPLE",
            "ai_tools": self.get_tools(),
        }

    # region static variables
    @staticmethod
    def get_description():
        return 'The task aims to hello to the user.'
    
    @staticmethod
    def get_task_type():
        return 'taskSayHello'
    
    @staticmethod
    def get_task_version():
        return '0.0.1'

    @staticmethod
    def get_system_prompt():
        return """You are an expert greeter, with an innate ability to say hello to the world in a succinct way."""
    
    # endregion static variables

    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return super().get_output_params_struct()

    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the task based on the user input.
        """
        # Alter input to try to format the response:
        engineering_prompt = """{{prompt}}"""
        # Alter the prompt to include the JSON template:
        self.user_prompt = user_prompt
        self.engineered_prompt = engineering_prompt.replace("{{prompt}}",user_prompt)
        return self.engineered_prompt
    
    def get_messages(self):
        """
        Get the messages for the task.
        """
        # This method should be overridden in subclasses to provide specific messages
        if self.engineered_prompt is None:
            raise ValueError("The prompt has not been engineered yet.")
        return [
            {"role": "user", "content": self.engineered_prompt},
        ]
    
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the task.
        """
        # This method should be overridden in subclasses to provide specific validation
        return True
    
    def hygiene_output(self, text_response):
        """
        Clean the output of the task.
        """
        return text_response
    
    def validate_output(self, text_response):
        """
        Validate the output of the task.
        """
        self.text_response = text_response
        return True
    
    @Task.record_step("completed")
    def complete_task(self):
        """
        Complete the task based of the values from the AI gnerated response.
        """
        # This method should be overridden in subclasses to provide specific completion tasks
        return self.task_id

    def next_task(self):
        """
        Choose the next task based on the current task.
        """
        # This method should be overridden in subclasses to provide specific next tasks
        return []

    def get_tools(self):
        """
        Get the tools for this task class or utility classes for the AI to consider using.
        """
        # This method should be overridden in subclasses to provide specific tools
        return []
    
    async def wait_on_dependency(self):
        """
        Wait for the Task to complete before proceeding.
        """
        # This method should be overridden in subclasses to provide specific waiting Tasks
        pass
    
    async def run(self, user_prompt):
        """
        Run the task with the provided prompt.
        """
        super().run(user_prompt)