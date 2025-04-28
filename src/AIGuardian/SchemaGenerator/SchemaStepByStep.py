
from anthropic import Anthropic

class SchemaStepByStep:
    """
    Class to generate a schema step by step based on user input.
    """

    def __intit__(self, user_request, ai_client=None, **kwargs):
        self.user_request = user_request
        self.ai_client = ai_client if ai_client else Anthropic()
        self.ai_system_prompt = kwargs.get("system_prompt", self.default_system_prompt())
        self.model = kwargs.get("model", "claude-3-haiku-latest")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 1000)
        self.top_p = kwargs.get("top_p", 0.9)
        self.schema = None

    def default_system_prompt(self):
        return """
        You are an expert data engineer, with an innate ability to build schemas for data architectures of business request/requirements.
        """

    def generate_table_list(self):
        """
        Generate a list of tables based on the user request.
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
        altered_prompt = engineering_prompt.replace("{{prompt}}",self.prompt)
        # Send the prompt to the AI client:
        message = self.ai_client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.0,
            system=self.ai_system_prompt,
            messages=[
            {"role": "user", "content": altered_prompt},
            {"role": "assistant", "content": "{"}
            ],
            stop_sequences=["}"]
        )
        # TODO add json validation and error handling, plus logging in SQLAlchemy to track inputs and responses.
        # TODO attempt start and stop tokens to guarantee the response is valid JSON.
        # TODO add a retry mechanism to try to get a valid JSON response.
        return message.content[0].text
    
    def generate_table_list_w_dtypes(self):
        """
        Generate a list of tables based on the user request.
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
            "columns":{"name":"column_name_1", "dataType":"Integer", "nullable":False, "metadata":"unique ID, short description of column",
            , "name":"column_name_2", "dataType":"String", "nullable":True, "metadata": "short description of column"
            , "name":"column_name_3", "dataType":"String", "nullable":False, "metadata": "short description of column"
            }},
        "table_name_2": {
            "purpose": "short description of tables usage in the architecture",
            "columns":
            {"name":"column_name_1", "dataType":"Integer", "nullable":False, "metadata": "unique ID, short description of column",
            , "name":"column_name_2", "dataType":"String", "nullable":True, "metadata":"short description of column"
            , "name":"column_name_3", "dataType":"Float", "nullable":True, "metadata": "short description of column"
            , "name":"column_name_4", "dataType":"Timestampe", "nullable":False, "metadata": "example: insert datetime column"
            }}
        }
        </JSON_Template>
        """
        # Alter the prompt to include the JSON template:
        altered_prompt = engineering_prompt.replace("{{prompt}}",self.prompt)
        # Send the prompt to the AI client:
        message = self.ai_client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.0,
            system=self.ai_system_prompt,
            messages=[
            {"role": "user", "content": altered_prompt},
            {"role": "assistant", "content": "{"}
            ],
            stop_sequences=["}"]
        )
        # TODO add json validation and error handling, plus logging in SQLAlchemy to track inputs and responses.
        # TODO attempt start and stop tokens to guarantee the response is valid JSON.
        # TODO add a retry mechanism to try to get a valid JSON response.
        return message.content[0].text
    
    def generate_table_columns(self, table_name):
        """
        Generate a list of columns for a specific table based on the user request.
        """
        prompt = self.ai_system_prompt()
        response = self.ai_client.generate_response(prompt, f"Generate columns for the table: {table_name}")
        return response
    
    def generate_column_schema(self, table_name, column_name):
        """
        Generate the schema for a specific column in a table based on the user request.
        """
        prompt = self.ai_system_prompt()
        response = self.ai_client.generate_response(prompt, f"Generate schema for the column: {column_name} in table: {table_name}")
        return response
    
    def combine_outputs(self, table_list, table_columns):
        """
        Combine the outputs of the table list and table columns into a final schema.
        """
        self.schema = {
            "tables": []
        }
        for table in table_list:
            columns = table_columns.get(table, [])
            self.schema["tables"].append({
                "table_name": table,
                "columns": columns
            })
        return self.schema
    
    @staticmethod
    def create_spark_schema(d_schema):
        """
        Create a Spark schema based on the generated schema.
        """
        spark_schema = []
        for table in self.schema["tables"]:
            table_name = table["table_name"]
            columns = table["columns"]
            spark_columns = []
            for column in columns:
                column_name = column["name"]
                data_type = column["dataType"]
                nullable = column["nullable"]
                metadata = column.get("metadata", {})
                spark_columns.append({
                    "name": column_name,
                    "dataType": data_type,
                    "nullable": nullable,
                    "metadata": metadata
                })
            spark_schema.append({
                "table_name": table_name,
                "columns": spark_columns
            })
        return spark_schema