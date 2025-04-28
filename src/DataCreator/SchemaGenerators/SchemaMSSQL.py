import json 
from pyspark.sql.types import *
from .SchemaGenerators import SchemaGenerator

class SchemaMSSQL(SchemaGenerator):
    """
    This class will be used to generate the schema of MSSQL tables backend.
    """

    @staticmethod
    def generate_schema(d_json):
        """
        This method will initiate the generation of the data for the data set.
        """
        return super().generate_schema(d_json)
    
    @staticmethod
    def generate_schema_sql(d_json):
        """
        This method will generate the dynamic SQL from the JSON schema.
        """
        """
        This method will generate the dynamic SQL from the JSON schema.
        """
        # Generate CREATE TABLE statements for each table
        table_schema = {}
        for table_name, table_info in d_json.items():
            columns = []
            primary_key = None
            
            # Process each column
            for column in table_info["columns"]:
                column_name = column["name"]
                data_type = SchemaGenerator.validate_dataType(column["dataType"])
                nullable = "NULL" if column.get("nullable", True) else "NOT NULL"
                
                # Check if this column is likely a primary key
                if "primary key" in column["metadata"].lower():
                    primary_key = column_name
                
                columns.append(f"    [{column_name}] {data_type} {nullable}")
            
            # Add primary key constraint if identified
            if primary_key:
                columns.append(f"    CONSTRAINT [PK_{table_name}] PRIMARY KEY CLUSTERED ([{primary_key}])")
            
            # Combine all column definitions
            columns_str = ",\n".join(columns)
            table_schema[table_name] = columns_str
        return table_schema
    
    @staticmethod
    def validate_dataType(data_type):
         """
        Validate the data type of a column.
        """
         valid_data_types = {
        "Integer": "INT",
        "String": "NVARCHAR(255)",
        "Float": "FLOAT",
        "Timestamp": "DATETIME2",
        "Boolean": "BIT",
        "JSON": "NVARCHAR(MAX)"
        }
         if data_type not in valid_data_types.keys():
            raise ValueError(f"Invalid data type: {data_type}. Valid data types are: {', '.join(valid_data_types.keys())}")
         return valid_data_types[data_type]
    
    @staticmethod
    def create_table(db_engine, table_name, schema):
        """
        Create a table in Spark with the given name and schema.
        """
        # Check if the schema is a string or StructType
        if isinstance(schema, str):
            pass  # Assuming schema is a SQL string, no need to create an empty DataFrame
        elif isinstance(schema, StructType):
            schema = SchemaMSSQL.generate_schema_sql(json.loads(schema.json()))
        else:
            raise ValueError(f"Schema should be a string or StructType, but was {type(schema)}")
        
        s_create_table = f"""
        if OBJECT_ID('dbo.{table_name}', 'U') IS NULL
        CREATE TABLE dbo.{table_name} ({schema})
        ;"""
        print('=' * 20)
        print(s_create_table)
        db_engine.execute(s_create_table)
        db_engine.commit()
        return f"Table {table_name} created with schema: {schema}"
