 
from abc import ABC, abstractmethod
from pyspark.sql.types import *

class SchemaGenerator(ABC):
    """
    Abstract base class for generating schemas for data sets.
    """

    @staticmethod
    @abstractmethod
    def generate_schema(d_json):
        """
        This method will initiate the generation of the data for the data set.
        Built of the JSON schema established by Spark standards: 
        https://spark.apache.org/docs/3.5.5/api/python/reference/pyspark.sql/api/pyspark.sql.types.StructType.html#pyspark.sql.types.StructType.fromJson
        """
        table_schema = {}
        for table_name, table_info in d_json.items():
            spark_columns = []
            columns = table_info.get("fields", table_info.get("columns", []))
            for column in columns:
                # schema = StructType.fromJson(schema)
                column = dict(column)
                if type(column) is not dict:
                    raise ValueError(f"Column for table key: {table_name} should be a dict, but was {type(column)}")
                if "name" not in column.keys() or "type" not in column.keys():
                    raise ValueError(f"Column for table key: {table_name} should have 'name' and 'type' keys, but was {column}")
                column["dataType"] = SchemaGenerator.validate_dataType(column.pop("type"))
                if 'metadata' in column.keys():
                    column['metadata'] = {"description": column.pop("metadata", "")} if type(column['metadata']) is str else column['metadata']
                spark_columns.append(StructField(**column))
            table_schema = {table_name: StructType(spark_columns)}
        return table_schema
    
    @staticmethod
    @abstractmethod
    def generate_schema_sql(d_json):
        """
        This method will generate the dynamic SQL from the JSON schema.
        """
        # Generate CREATE TABLE statements for each table
        table_schema = {}
        for table_name, table_info in d_json.items():
            columns = []
            primary_key = None
            
            columns_json = table_info.get("fields", table_info.get("columns", []))
            # Process each column
            for column in columns_json:
                column_name = column["name"]
                data_type = SchemaGenerator.validate_dataType(column["type"])
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
    @abstractmethod
    def validate_dataType(data_type):
        """
        Validate the data type of a column.
        """
        valid_data_types = {
            "Boolean": BooleanType(),
            "Byte": ByteType(),
            "Short": ShortType(),
            "Integer": IntegerType(),
            "Long": LongType(),
            "Float": FloatType(),
            "Double": DoubleType(),
            "String": StringType(),
            "JSON": StringType(),
            "Binary": BinaryType(),
            "Date": DateType(),
            "Timestamp": TimestampType(),
            # "Array": ArrayType(elementType),
            # "Map": MapType(keyType, valueType, valueContainsNull),
            # "Struct": StructType(fields),
            # "StructField": StructField(name, dataType, nullable),
            # "Decimal": DecimalType(precision, scale),
            "Null": NullType(),
            # "CalendarInterval": CalendarIntervalType(),
            "YearMonthInterval": YearMonthIntervalType(),
            "DayTimeInterval": DayTimeIntervalType(),
            # "UserDefined": UserDefinedType(userClass)
        }
        if data_type not in valid_data_types.keys():
            raise ValueError(f"Invalid data type: {data_type}. Valid data types are: {', '.join(valid_data_types.keys())}")
        return valid_data_types[data_type]
    
    @staticmethod
    @abstractmethod
    def create_table(db_engine, table_name, schema):
        """
        Create a table in Spark with the given name and schema.
        """
        # Check if the schema is a string or StructType
        if isinstance(schema, str):
            db_engine.sql(f"""
            CREATE TABLE IF NOT EXIST {table_name} ({schema})
            """)
        elif isinstance(schema, StructType):
            empty_df = db_engine.createDataFrame([], schema)
            empty_df.write.mode("overwrite").saveAsTable(table_name)
        else:
            raise ValueError(f"Schema should be a string or StructType, but was {type(schema)}")
        
        return f"Table {table_name} created with schema: {schema}"
    
    @classmethod
    @abstractmethod
    def create_tables_from_dict(cls, db_engine, d_tables):
        """
        Create tables in Spark from a list of table names and schemas.
        """
        for table_name, schema in d_tables.items():
            cls.create_table(db_engine, table_name, schema)
        return f"Tables created: {', '.join(d_tables.keys())}"