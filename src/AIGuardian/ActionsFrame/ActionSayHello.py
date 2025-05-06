from abc import ABC, abstractmethod
import datetime
import json
from ..ActionsFrame.Action import Action
from ..ActionsFrame.ActionExceptions import ValidateAIResponseError
from ...DataCreator.SchemaGenerators.SchemaMSSQL import SchemaMSSQL

@Action.register("ActionSayHello")
class ActionSayHello(Action):

    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_action=None):
        self.input_params = input_params
        super().__init__(input_params=input_params, sequence_limit=sequence_limit, verbose=verbose, parent_action=parent_action)
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
        return 'The action aims to hello to the user.'
    
    @staticmethod
    def get_action_type():
        return 'ActionSayHello'
    
    @staticmethod
    def get_action_version():
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
        Generate a prompt for the action based on the user input.
        """
        # Alter input to try to format the response:
        engineering_prompt = """{{prompt}}"""
        # Alter the prompt to include the JSON template:
        self.user_prompt = user_prompt
        self.engineered_prompt = engineering_prompt.replace("{{prompt}}",user_prompt)
        return self.engineered_prompt
    
    def get_messages(self):
        """
        Get the messages for the action.
        """
        # This method should be overridden in subclasses to provide specific messages
        if self.engineered_prompt is None:
            raise ValueError("The prompt has not been engineered yet.")
        return [
            {"role": "user", "content": self.engineered_prompt},
        ]
    
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the action.
        """
        # This method should be overridden in subclasses to provide specific validation
        return True
    
    def hygiene_output(self, text_response):
        """
        Clean the output of the action.
        """
        return text_response
    
    def validate_output(self, text_response):
        """
        Validate the output of the action.
        """
        self.text_response = text_response
        return True
    
    @Action.record_step("Complete Action")
    def complete_action(self):
        """
        Complete the action based of the values from the AI gnerated response.
        """
        # This method should be overridden in subclasses to provide specific completion actions
        return self.action_id

    def next_action(self):
        """
        Choose the next action based on the current action.
        """
        # This method should be overridden in subclasses to provide specific next actions
        return []

    def get_tools(self):
        """
        Get the tools for this action class or utility classes for the AI to consider using.
        """
        # This method should be overridden in subclasses to provide specific tools
        return []
    
    def run(self, user_prompt):
        """
        Run the action with the provided prompt.
        """
        super().run(user_prompt)