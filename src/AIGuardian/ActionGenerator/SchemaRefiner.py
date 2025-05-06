import json
from ..ActionsFrame.Action import Action
from ..ActionGenerator.ActionGenerator import ActionGenerator
from ..ActionGenerator.ColumnRefiner import ColumnRefiner


class SchemaRefiner(ActionGenerator):
    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_action=None):
        super().__init__(input_params, sequence_limit, verbose, parent_action)

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
    
    @classmethod
    def from_json(cls, json_schema):
        """
        Create a SchemaRefiner object from a JSON schema.
        """
        json_dict = json.loads(json_schema)
        ls_table_keys = ['purpose', 'fields']
        ls_fields_keys = ['name', 'description', 'data_type']
        # iterate over each table, which is reprented by each key in the json_dict
        # for key, val in json_dict.items():
        #     # confirm the value is a dictionary
        #     if isinstance(val, dict):
        #         # Check the val dictionary has the fields and purpose keys
        #         st_overlap = set(val.keys()) & set(ls_table_keys)
        #         if len(st_overlap) == len(ls_table_keys):
        #             # Check each field has the minimum key set
        #             for fields_val in val['fields'].values():
        #                 if isinstance(fields_val, dict):
        #                     st_overlap = set(fields_val.keys()) & set(ls_fields_keys)
        #                     if len(st_overlap) != len(ls_fields_keys):
        #                         raise ValueError(f"Invalid field schema for table {key}: {fields_val}")
        #                 else:
        #                     raise ValueError(f"Invalid field schema for table {key}: {fields_val}")
        #         else:
        #             raise ValueError(f"Invalid minimum keys for table {key}: is missing {set(ls_table_keys) - st_overlap}")
        #     else:
        #         raise ValueError(f"Invalid structure for table {key} should be a dictionarym but is {type(val)}")

        #         for sub_key in val.keys():
        #             if sub_key not in ['purpose', 'columns']
        # return cls(schema=json_schema)
    
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
        for table_name, table_info in self.input_params.items():
            if isinstance(table_info, dict):
                # Generate actions for each table and its fields
                action_parameters = {
                    "table_name": table_name,
                    "purpose": table_info["purpose"],
                    "fields": table_info["fields"]
                }
                action = ColumnRefiner(action_parameters)
                self.child_action.append(action)
        return self.child_action
    
    @Action.record_step("COMPLETED")
    def complete_action(self):
        # Loop through the child actions and rebuild the schema.
        d_tables = {}
        for action in self.child_action:
            if isinstance(action, ColumnRefiner):
                d_tables = {**d_tables, **action.output_params}
        self.output_params = d_tables
        return self.output_params

    def run(self, user_prompt):
        """
        Run the code to generate schema refinement actions.
        """
        if self._step_name_code < 100:
            self.initialize()
        for action in self.geneterate_actions():
            user_prompt = self.parent_action.user_prompt if self.parent_action else ""
            action.run(user_prompt)
        # Combine processing into final output
        self.complete_action()

    # region Action Methods
