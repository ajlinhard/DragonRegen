
from pyspark.sql.types import *
from ..DataGenerators.PyDataGenerators import PyDataGenerators
from .ColGenerator import ColGenerator

class ColBaseGenerator(ColGenerator):
    """
    Abstract base class for generating columns in a DataFrame.
    """
    def __init__(self, name:str, dataType:DataType=StringType(), nullalbe:bool=True, metadata:dict=None):
        """
        Initialize the column generator.

        Parameters:
        spark_session (SparkSession): The Spark session to use.
        schema (StructField): The schema for the column.
        """
        self.name = name
        self.dataType = dataType
        self.nullable = nullalbe
        self.metadata = self.set_metadata(metadata)

    @classmethod
    def replicate(cls, o_field:StructField):
        """
        Replicate the column generator.

        Parameters:
        sparkSession (SparkSession): The Spark session to use.
        o_field (StructField): The schema for the column.

        Returns:
        ColGenerator: An instance of the column generator.
        """
        return cls(o_field.name, o_field.dataType, o_field.nullable, o_field.metadata)

    def generate_column(self, i_row_count: int) -> list:
        """
        Generate a column of data based on the specified schema.

        Parameters:
        num_rows (int): Number of rows to generate.
        schema (StructField): Schema for the column.

        Returns:
        list: Generated column data.
        """
        return super().generate_column(i_row_count)

    def set_metadata(self, metadata:dict):
        """
        Set the metadata for the column. Allow for overriding for complex col generators.

        Parameters:
        metadata (dict): Metadata for the column.
        """
        return super().set_metadata(metadata)

    @property
    def ColField(self) -> StructField:
        """
        Get the StructField for the column.

        Returns:
        StructField: The schema for the column.
        """
        return StructField(self.name, self.dataType, self.nullable, self.metadata)
    
    @ColField.setter
    def ColField(self, value:StructField):
        """
        Set the StructField for the column.

        Parameters:
        value (StructField): The schema for the column.
        """
        if not isinstance(value, StructField):
            raise ValueError("value must be a StructField")
        self.name = value.name
        self.dataType = value.dataType
        self.nullable = value.nullable
        self.metadata = value.metadata
        