
class SchemaBuilder:
    def __init__(self):
        self.ai_client = None
        self.user_request = None
        self.schema = None

    def prep_init_prompt(self):
        # TODO make the list generated of the registry or factor. Store definition in class.
        return """Please prepare a list of schema column objects to generate for off the <column_list> below. Format the output like the examples <output_example> below:
        <column_list>
        - Unique_ID: A unique identifier for each row in the table.
        - Categorical: A column with a predefined set of values "column_values", example: Apple, Banana, Orange.
        - Integer: A column with whole numbers of any postive or negative value.
        - Float: A column with decimal numbers of any positive or negative value.
        - Date: A column with date values in the format YYYY-MM-DD.
        - Time: A column with time values in the format HH:MM:SS.
        - DateTime: A column with date and time values in the format YYYY-MM-DD HH:MM:SS.
        - String: A column with text values of any length.
        - Boolean: A column with True or False values.
        - First_Name: A column with first names of individuals.
        - Last_Name: A column with last names of individuals.
        </column_list>

    <output_example>
    Example 1: 
    Input: 
    Output: [Unique_ID]
"""