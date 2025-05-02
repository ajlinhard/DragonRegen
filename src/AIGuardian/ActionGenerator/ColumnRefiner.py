import json

class SchemaRefiner:
    def __init__(self, schema):
        self.schema = schema

    @classmethod
    def from_json(cls, json_schema):
        """
        Create a SchemaRefiner object from a JSON schema.
        """
        json_dict = json.loads(json_schema)
        ls_table_keys = ['purpose', 'fields']
        ls_fields_keys = ['name', 'description', 'data_type']
        # iterate over each table, which is reprented by each key in the json_dict
        for key, val in json_dict.items():
            # confirm the value is a dictionary
            if isinstance(val, dict):
                # Check the val dictionary has the fields and purpose keys
                st_overlap = set(val.keys()) & set(ls_table_keys)
                if len(st_overlap) == len(ls_table_keys):
                    # Check each field has the minimum key set
                    for fields_val in val['fields'].values():
                        if isinstance(fields_val, dict):
                            st_overlap = set(fields_val.keys()) & set(ls_fields_keys)
                            if len(st_overlap) != len(ls_fields_keys):
                                raise ValueError(f"Invalid field schema for table {key}: {fields_val}")
                        else:
                            raise ValueError(f"Invalid field schema for table {key}: {fields_val}")
                else:
                    raise ValueError(f"Invalid minimum keys for table {key}: is missing {set(ls_table_keys) - st_overlap}")
            else:
                raise ValueError(f"Invalid structure for table {key} should be a dictionarym but is {type(val)}")

                for sub_key in val.keys():
                    if sub_key not in ['purpose', 'columns']
        return cls(schema=json_schema)
    
    def geneterate_actions(self):
        """
        Generate actions based on the schema.
        """
        ls_actions = []
        for table_name, table_info in self.schema.items():
            # Generate actions for each table and its fields
            action_parameters = {
                "table_name": table_name,
                "purpose": table_info["purpose"],
                "fields": table_info["fields"]
            }
            action = 
            ls_actions.append(action)