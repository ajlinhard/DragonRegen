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
        # Generate CREATE TABLE statements for each table
        d_json = dict(d_json)
        table_schema = {}
        for table_name, table_info in d_json.items():
            columns = []
            primary_key = None
            
            # Process each column
            for column in table_info.get("fields", table_info.get("columns", [])):
                column_name = column["name"]
                data_type = SchemaMSSQL.validate_dataType(column.get("type", column.get("dataType")))
                nullable = "NULL" if column.get("nullable", True) else "NOT NULL"
                column_def_str = f"    [{column_name}] {data_type} {nullable}"
                # Check if this column is likely a primary key
                if "primary_key" in column["metadata"].keys() or "primary key" in column["metadata"].get("description", "").lower():
                    column_def_str += " IDENTITY(1,1)"
                    primary_key = column["metadata"].get("primary_key", None)
                
                columns.append(column_def_str)
            
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
        "String": "NVARCHAR(MAX)",
        "Float": "FLOAT",
        "Timestamp": "DATETIME2",
        "Boolean": "BIT",
        "JSON": "NVARCHAR(MAX)"
        }
         
         spark_to_mssql_type_mapping = {
            # Numeric types
            "ByteType": "TINYINT",
            "ShortType": "SMALLINT",
            "IntegerType": "INT",
            "LongType": "BIGINT",
            "FloatType": "REAL",
            "DoubleType": "FLOAT",
            "DecimalType": "DECIMAL",
            
            # String types
            "StringType": "NVARCHAR(255)",
            "VarcharType": "VARCHAR",
            "CharType": "CHAR",
            
            # Binary types
            "BinaryType": "VARBINARY(MAX)",
            
            # Boolean type
            "BooleanType": "BIT",
            
            # Datetime types
            "TimestampType": "DATETIME2",
            "DateType": "DATE",
            
            # Complex types
            "ArrayType": "NVARCHAR(MAX)",
            "MapType": "NVARCHAR(MAX)",
            "StructType": "NVARCHAR(MAX)",
            
            # Others
            "NullType": "NVARCHAR(MAX)",
            "JSON": "NVARCHAR(MAX)",
            "Interval": "NVARCHAR(MAX)",
            
            # Extended types (not native Spark but commonly used)
            "GUID": "UNIQUEIDENTIFIER",
            "SmallDateTime": "SMALLDATETIME",
            "Money": "MONEY",
            "SmallMoney": "SMALLMONEY",
            "Text": "TEXT",
            "NText": "NTEXT",
            "Image": "IMAGE",
            "XML": "XML",
            "TimeType": "TIME",
            "Geography": "GEOGRAPHY",
            "Geometry": "GEOMETRY",
            "HierarchyID": "HIERARCHYID"
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
