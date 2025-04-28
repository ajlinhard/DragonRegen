from pyspark.sql.types import *
from .SchemaGenerators import SchemaGenerator

class SchemaSpark(SchemaGenerator):
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
        pass