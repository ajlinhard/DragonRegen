import json
from ..ActionsFrame.Action import Action
from ..ActionGenerator.ActionGenerator import ActionGenerator
from ..ActionsFrame import DataColumnType, DataColumnRefiner
from ..AIUtils.GenAIUtils import GenAIUtils

class ColumnRefiner(ActionGenerator):
    def __init__(self, input_params, schema):
        self.schema = schema
        super().__init__(input_params)

    # region static variables
    @staticmethod
    def get_description():
        return """Create a set of sub-actions to refine the schema with more details."""
    
    @staticmethod
    def get_action_type():
        return 'schema'
    
    @staticmethod
    def get_action_version():
        return '0.0.1'

    # endregion static variables
    
    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return {
            "output_type": GenAIUtils.valid_output_type("ActionList"),
            "output_struct": [ColumnRefiner],
        }
    
    # region Action Methods
    def geneterate_actions(self):
        """
        Generate actions based on the schema.
        """
        self.child_action = [] if self.child_action is None else self.child_action
        table_name = self.input_params.get("table_name")
        table_purpose = self.input_params.get("purpose")
        for col_name, col_description in self.input_params.items():
            # Generate actions for each table and its fields
            action_parameters = {
                "table_name": table_name,
                "purpose": table_purpose,
                "column_name": col_name,
                "description": col_description,
            }
            action_1 = DataColumnType(action_parameters)
            self.child_action.append(action_1)
            action_2 = DataColumnRefiner(action_parameters, parent_action=action_1)
            self.child_action.append(action_2)
        return self.child_action
    
    def complete_action(self):
        # Loop through the child actions and rebuild the schema.
        ls_fields = []
        for action in self.child_action:
            if isinstance(action, DataColumnRefiner):
                ls_fields.append(action.output_params)
        self.output_params = {self.input_params.get("table_name"):
                {"purpose": self.input_params.get("purpose"), "fields": ls_fields}}
        return self.output_params

    def run(self, user_prompt):
        """
        Run the code to generate schema refinement actions.
        """
        for action in self.geneterate_actions():
            user_prompt = self.parent_action.user_prompt if self.parent_action else ""
            action.run(user_prompt)
        # Loop through the child actions and rebuild the schema.


    # endregion Action Methods
    