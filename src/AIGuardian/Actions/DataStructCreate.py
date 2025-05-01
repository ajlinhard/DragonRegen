from abc import ABC, abstractmethod
import datetime
import json
from ..Actions.Action import Action
from ..Actions.ActionExceptions import ValidateAIResponseError
from ...DataCreator.SchemaGenerators.SchemaMSSQL import SchemaMSSQL

@Action.register("DataStructCreate")
class DataStructCreate(Action):

    def __init__(self, parameters=None):
        self.parameters = parameters
        super().__init__(parameters=parameters)

    @classmethod
    def from_parent_action(cls, parent_action):
        """
        Create a new action from a parent action.
        """
        new_action = cls(
            parameters=cls.potential_parameters(parent_action.parameters),
        )
        new_action.parent_action = parent_action
        new_action.group_action_id = parent_action.action_id
        new_action.sequence = parent_action.sequence + 1
        new_action.set_action_id()
        return new_action

    # region static variables
    @staticmethod
    def get_description():
        return 'The action aims to create a data system structure relavent to the users requet. Complete with tables, columns, data types.'
    
    @staticmethod
    def get_action_type():
        return 'DataStructCreate'
    
    @staticmethod
    def get_action_version():
        return '0.0.1'

    @staticmethod
    def get_system_prompt():
        return """You are an expert data engineer, with an innate ability to build schemas for data architectures of business request/requirements."""
    
    # endregion static variables

    @staticmethod
    def potential_parameters(parameters):
        """
        Generate potential parameters for the action.
        """
        # This method should be overridden in subclasses to provide specific parameters

        return parameters

    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the action based on the user input.
        """
        # Alter input to try to format the response:
        engineering_prompt = """Please take the following <business_requirements> and create the table list and schema for the the request.
        <business_requirements>
        {{prompt}}
        </business_requirements>
        Please provide the response in a JSON format like the <JSON_Template> below:
        <JSON_Template>
        {"table_name_1": {
            "purpose": "short description of tables usage in the architecture",
            "columns":{"column_name_1": "unique ID, short description of column",
            , "column_name_2": "short description of column"
            , "column_name_3": "short description of column"
            }},
        "table_name_2": {
            "purpose": "short description of tables usage in the architecture",
            "columns":
            {"column_name_1": "unique ID, short description of column",
            , "column_name_2": "short description of column"
            , "column_name_3": "short description of column"
            , "column_name_4": "short description of column"
            }}
        }
        </JSON_Template>
        """
        # Alter the prompt to include the JSON template:
        self.engineered_prompt = engineering_prompt.replace("{{prompt}}",user_prompt)
        return self.engineered_prompt
    
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
        # Check if the last and first characters are brackets
        if text_response[0] != '{':
            # Remove the first and last characters
            text_response = '{' + text_response
        if text_response[-1] != '}':
            text_response += '}'
        return text_response
    
    def validate_output(self, text_response):
        """
        Validate the output of the action.
        """
        try:
            json.loads(text_response)
            return True
        except json.JSONDecodeError as e:
            # Get error position
            pos = e.pos
            # Calculate start and end positions for context
            start = max(0, pos - 10)
            end = min(len(text_response), pos + 10)
            # Extract the context around the error
            context = text_response[start:end]
            new_error_msg = f"Error message: {str(e)}" + \
                f"Error position: line {e.lineno}, column {e.colno}" + \
                f"Error Line Context: {context}" + \
                f"Error document: {e.doc}"
            raise ValidateAIResponseError(new_error_msg)
        return False
    
    def complete_action(self):
        """
        Complete the action based of the values from the AI gnerated response.
        """
        # This method should be overridden in subclasses to provide specific completion actions
        self.log_action()
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
        return [SchemaMSSQL.create_table]