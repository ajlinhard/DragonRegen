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

from src.AIGuardian.AIUtils.GenAIUtils import GenAIUtils
from src.AIGuardian.AIDataModels.AILogs import TaskLog, TaskArtifact, LLMRequest
from src.AIGuardian.Tasks.TaskAI import TaskAI
from src.AIGuardian.Tasks.TaskRegistry import TaskRegistry
from src.AIGuardian.Tasks.TaskExceptions import ValidateAIResponseError
from src.DataCreator.SchemaGenerators.SchemaMSSQL import SchemaMSSQL
from src.DataCreator.ColGenerators import *
from src.DataCreator.ColGenerators.ColGenRegistry import ColGenRegistry

@TaskRegistry.register("DataColumnType")
class DataColumnType(TaskAI):

    def __init__(self, input_params: dict={}, sequence_limit=10, verbose=False, parent_task=None):
        self.input_params = input_params
        super().__init__(input_params=input_params, sequence_limit=sequence_limit, verbose=verbose, parent_task=parent_task)
        self.model_parameters = {"max_tokens": 10000,
            "temperature": 0.1,
            "stop_sequences": ["</JSON_Template>"],
            "pref_model_type": "COMPLEX",
            "ai_tools": self.get_tools(),
        }

    # region static variables
    @staticmethod
    def get_description():
        return 'The task aims to what type of data is in the column for choosing the additional column metadata details'
    
    @staticmethod
    def get_task_type():
        return 'DataColumnType'
    
    @staticmethod
    def get_task_version():
        return '0.0.1'

    @staticmethod
    def get_system_prompt():
        return """You are an expert data engineer, with an innate ability to build schemas for data architectures of business request/requirements."""
    
    # endregion static variables

    # region task Methods
    def engineer_prompt(self, user_prompt=None):
        """
        Generate a prompt for the task based on the user input.
        """
        # Alter input to try to format the response:
        engineering_prompt = """Please take the following <column_information> to choose what type of column a column most likely is.
<column_information>
Table Purpose: {{purpose}}
Column Info: "{{column_name}}": "{{description}}"
</column_information>

Choose one column_type from this list <choices> below, structure as column_type: description of what qualifies a column as that type.
<choices>
"""+ '\n'.join([str(key)+': '+str(val) for key, val in ColGenRegistry.get_all_descriptions().items()])+"""
Unique_Identifier: A unique identifier for each record, typically a primary key.
City: A column that stores the name of a city.
Email: A column that stores email addresses, often used for contact information.
Integer: A column that stores whole numbers, often used for counts or identifiers.
Date: A column that stores date values, typically representing a specific point in time.
Boolean: A column that stores true/false values, often used for flags or binary states.
Text: A column that stores free-form text or descriptions.
Numeric: A column that stores decimal or floating-point numbers, often used for measurements or financial data.
</choices>
Respond in JSON format like this:
{
    "choice": "selected_option",
    "reason": "brief explanation"
}

<Examples>
Example 1:
<column_information>
Table Purpose: Stores information about gym members.
Column Info: "member_name": "The first name of the gym member."
</column_information>
Output:
<JSON_Template>
{
    "choice": "First_Name",
    "reason": "This represents the first name of a person, which is a common attribute in member records."
}
</JSON_Template>

Example 2:
<column_information>
Table Purpose: Stores information about gym members.
Column Info: "subscription": "The type of subscription the member has."
</column_information>
Output:
<JSON_Template>
{{
    "choice": "Categorical",
    "reason": "There is a finite number of options for memberships at a gym."
}}
</JSON_Template>
</Examples>"""
        # Alter the prompt to include the JSON template:
        self.user_prompt = user_prompt
        # list out subsitution keys allowed/expected for the prompt
        sub_keys = ["purpose", "column_name", "description"]
        subs_vals = {key: val for key, val in self.input_params.items() if key in sub_keys}
        # replace the keys in the prompt with the values from the input_params
        self.engineered_prompt = GenAIUtils.prompt_dict_substitute(engineering_prompt, **self.input_params)
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
    
    def complete_task(self):
        """
        Complete the task based of the values from the AI gnerated response.
        """
        self.output_params = json.loads(self.text_response)
        self.output_params['col_type'] = self.output_params.pop('choice')
        # Write the message as a new TaskArtifact
        data_row = {
            "task_id": self.task_id,
            "group_task_id": self.group_task_id,
            "insert_dt": datetime.datetime.now().isoformat(),
            "name": 'Column Type',
            "description": self.input_params.get("description", ""),
            "parts": [self.output_params],
            "metadata": self.model_parameters,
            "extensions": None   
        }
        self.output_artifacts.append(TaskArtifact(**data_row))
        # Check if the response is valid
        self.is_completed = True
        return super().complete_task()
    
    # endregion task Methods
