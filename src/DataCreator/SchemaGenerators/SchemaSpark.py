from pyspark.sql.types import *
from .SchemaGenerators import SchemaGenerator

class SchemaSpark(SchemaGenerator):
    """
    This class will be used to generate the schema of MSSQL tables backend.
    """
    