from abc import ABC, abstractmethod
import datetime
import json
from ..AIUtils.GenAIUtils import GenAIUtils
from ..ActionsFrame.Action import Action
from ..ActionsFrame.ActionExceptions import ValidateAIResponseError
from ...DataCreator.SchemaGenerators.SchemaMSSQL import SchemaMSSQL

@Action.register("DataStructCreate")
class DataStructCreate(Action):

    def __init__(self, input_params=None):
        self.input_params = input_params
        super().__init__(parameters=parameters)
        self.model_parameters = {"max_tokens": 10000,
            "temperature": 0.1,
            "stop_sequences": ["</JSON_Template>"],
            "pref_model_type": "COMPLEX",
            "ai_tools": self.get_tools(),
        }

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

    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return {
            "output_type": GenAIUtils.valid_output_type("JSON"),
            "output_struct": ,
        }

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
            "fields":{"column_name_1": "unique ID, short description of column",
            , "column_name_2": "short description of column"
            , "column_name_3": "short description of column"
            }},
        "table_name_2": {
            "purpose": "short description of tables usage in the architecture",
            "fields":
            {"column_name_1": "unique ID, short description of column",
            , "column_name_2": "short description of column"
            , "column_name_3": "short description of column"
            , "column_name_4": "short description of column"
            }}
        }
        </JSON_Template>
        """
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
            {"role": "assistant", "content": "<JSON_Template>\n{"}
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
        return GenAIUtils.hygiene_to_json(text_response)
    
    def validate_output(self, text_response):
        """
        Validate the output of the action.
        """
        try:
            json.loads(text_response)
            self.text_response = text_response
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
    
    def run(self, user_prompt):
        """
        Run the action with the given user prompt.
        """
        super().run(user_prompt)