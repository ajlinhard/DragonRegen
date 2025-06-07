from abc import ABC, abstractmethod
import datetime
import json
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskState,
)
from pydantic import BaseModel, Field

from src.AIGuardian.AIUtils.GenAIUtils import GenAIUtils
from src.AIGuardian.Tasks.Task import Task
from src.AIGuardian.Tasks.TaskRegistry import TaskRegistry
from src.AIGuardian.Tasks.TaskExceptions import ValidateAIResponseError
from src.DataCreator.SchemaGenerators.SchemaMSSQL import SchemaMSSQL
from src.DataCreator.ColGenerators import *
from src.DataCreator.ColGenerators.ColGenRegistry import ColGenRegistry
from src.AIGuardian.AIDataModels.AILogs import TaskLog, TaskArtifact

class InputParams(BaseModel):
    """
    Represents the input parameters for the DataColumnRefiner task.
    """
    col_type: str = Field(default="ColBasic", description="The type of column to be refined.")
    column_name: str = Field(..., description="The name of the column to be refined.")
    description: str = Field(...,description="A brief description of the column's purpose.")
    purpose: str = Field(...,description="The purpose of the table to which the column belongs.")

@TaskRegistry.register("DataColumnRefiner")
class DataColumnRefiner(Task):

    def __init__(self, input_params={}, sequence_limit=10, verbose=False, parent_task=None):
        self.input_params = InputParams(**input_params)
        super().__init__(input_params=input_params, sequence_limit=sequence_limit, verbose=verbose, parent_task=parent_task)
        self.model_parameters = {"max_tokens": 10000,
            "temperature": 0.1,
            "stop_sequences": ["</JSON_Template>"],
            "pref_model_type": "COMPLEX",
        }

    # region static variables
    @staticmethod
    def get_description():
        return 'The task aims to create a data system structure relavent to the users requet. Complete with tables, columns, data types.'
    
    @staticmethod
    def get_task_type():
        return 'DataColumnRefiner'
    
    @staticmethod
    def get_task_version():
        return '0.0.1'

    @staticmethod
    def get_system_prompt():
        return """You are an expert data engineer, with an innate ability to build schemas for data architectures of business request/requirements."""
    
    # endregion static variables

    def column_type_JSON(self):
        """
        Using the DataCreator column generators with the inpout parameters, generate a JSON representation of the column type.
        """
        # TODO Implement code so the next 4 lines of code will acuatlly work.
        o_generator = ColGenRegistry.get_col_generator(self.input_params.col_type)
        col_type_json = o_generator.get_metadata_json()
        return {"name": "example_column", "type": "Integer", "nullable": True, "metadata": col_type_json}

    def column_type_examples(self):
        """
        Using the DataCreator column generators with the inpout parameters, generate a JSON Example of the column type.
        """
        o_generator = ColGenRegistry.get_col_generator(self.input_params.col_type)
        return o_generator.get_examples()
    
    # region task Methods
    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the task based on the user input.
        """
        # Alter input to try to format the response:
        engineering_prompt = """Please take the following <column_information> to fill in JSON values and only use keys in "metadata" from <JSON_Template>.
        <column_information>
        Table Purpose: {{purpose}}
        Column Info: "{{column_name}}": "{{description}}"
        </column_information>
        Please provide the response in a JSON format like the <JSON_Template> below. If the JSON value has (Optional) in the value you may or may not included.
        There are examples below at <Examples>.
        <JSON_Template>
        """+ json.dumps(self.column_type_JSON()) +"""
        </JSON_Template>

        <Examples>
        """+self.column_type_examples()+"""
        </Examples>"""
        # Alter the prompt to include the JSON template:
        self.user_prompt = user_prompt
        self.engineered_prompt = GenAIUtils.prompt_dict_substitute(engineering_prompt, **self.input_params.model_dump())
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
            {"role": "assistant", "content": "<JSON_Template>\n{"}
        ]
    
    def hygiene_output(self, text_response):
        """
        Clean the output of the task.
        """
        return GenAIUtils.hygiene_to_json(text_response)

    def validate_output(self, text_response):
        """
        Validate the output of the task.
        """
        return GenAIUtils.validate_json(text_response)
    
    def receive_artifact(self, artifact):
        """
        Receive an artifact from the AI response. This task expects an artifact of type 'Column Type'.
        """
        artifact_name = artifact.name
        parts_list = artifact.parts
        for part in parts_list:
            if isinstance(part, str):
                part = json.loads(part)
            if artifact_name == "Column Type":
                self.input_params.col_type = part.get("col_type", self.input_params.col_type)
            
    
    def complete_task(self):
        """
        Complete the task based of the values from the AI gnerated response.
        """
        self.output_params = json.loads(self.text_response)
        self.output_params["metadata"]["col_type"] = self.input_params.get("col_type", None)
        # Check if the response is valid
        self.is_completed = True
        return super().complete_task()
    
    # endregion task Methods
