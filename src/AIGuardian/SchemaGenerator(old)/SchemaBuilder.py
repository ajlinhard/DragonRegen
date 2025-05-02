
class SchemaBuilder:
    def __init__(self):
        self.ai_client = None
        self.user_request = None
        self.schema = None

    def ai_system_prompt(self):
        return """You are an expert data engineer, with an innate ability to build schemas for data architectures of business request/requirements.
        The number of tables may or may not be explained in the request. OLTP scenarios are usually more tables and OLAP or DSS scenarios are usally less tables that are wider.
        The schema should be in JSON format and should include the following fields:
        - name: The name of the column.
        - dataType: The data type of the column.
        - nullable: Whether the column can contain null values.
        - metadata: Any additional metadata for the column.
        """

    def prep_init_prompt(self):
        # TODO make the list generated of the registry or factor. Store definition in class.
        """ TODO also  make sense to make it work step-by-step
        1. How many tables are estimated to be needed?
        2. Name the tables and their purpose.
        3. What are the columns needed for each table with a description?
        4. Iterate over and generate the columns JSON.
        """
        return """Please prepare a list of schema column objects to generate for off the <column_list> below. Format the output like the examples <output_examples> below:
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

        <Instructions>
        Think throught the requirements step by step and generate the schema in JSON format. 
        
        Consider the following:
        - Does the problem require unique IDs for each row, or foriegn keys to other tables?
        - For foriegn keys or other IDs, are relatoinships expressed to other columns or tables?
        - For the problem described what other columns are needed to solve the problem potentially?
        </Instructions>

    <output_examples>
    Example 1: 
    Input: Create a table for an insurance company quoting transaction system.
    Output: {
    {"name":"Quote_ID","dataType":"Integer","nullable":false,"metadata":{"description":"A unique identifier for each quote."}
    ,{"name":"Customer_ID","dataType":"Integer","nullable":false,"metadata":{"description":"A unique identifier for each customer on there household, which is a rough composite of Last Name and Address."}
    ,{"name":"Quote_Date","dataType":"DateTime","nullable":false,"metadata":{"description":"The date and time when the quote was created."}
    ,{"name":"Quote_Amount","dataType":"Float","nullable":true,"metadata":{"description":"The amount of the quote."}
    ,{"name":"Quote_Status","dataType":"Categorical","nullable":false,"metadata":{"description":"The status of the quote (e.g., pending, accepted, rejected)."}}
    ,{"name":"Customer_First_Name","dataType":"String","nullable":false,
        "metadata":{"description":"The first name of the customer."
            ,"ColType":"Fist_Name" 
        }
    }
    ,{"name":"Customer_Last_Name","dataType":"String","nullable":false,
        "metadata":{"description":"The last name of the customer.",
            ,"ColType":"Last_Name" 
        }
    }
    ,{"name":"Customer_Address","dataType":"String","nullable":true,"metadata":{"description":"The address of the customer."}
    ,{"name":"Customer_City","dataType":"String","nullable":true,"metadata":{"description":"The city of the customer."}
    ,{"name":"Customer_State","dataType":"String","nullable":true,"metadata":{"description":"The state of the customer."}
    ,{"name":"Customer_Zip","dataType":"String","nullable":true,"metadata":{"description":"The zip code of the customer."}
    ,{"name":"Customer_Phone","dataType":"String","nullable":true,"metadata":{"description":"The phone number of the customer."}
    ,{"name":"Insurance_Type","dataType":"Categorical","nullable":true,
        "metadata":{"description":"The type of insurance (e.g., auto, home, life)."
            ,"column_values":["auto","home","life"]
            ,"ColType":"Categorical"
        }
    }
    ,{"name":"Policy_Number","dataType":"String","nullable":true,"metadata":{"description":"The policy number associated with the quote."}
    ,{"name":"Insert_Date","dataType":"DateTime","nullable":false,"metadata":{"description":"The date and time when the quote was inserted into the system."}
    ,{"name":"Update_Date","dataType":"DateTime","nullable":true,"metadata":{"description":"The date and time when the quote was last updated."}
    }
    </output_examples>
"""