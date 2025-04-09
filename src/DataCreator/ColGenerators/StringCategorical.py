
from pyspark.sql.types import *
from ..DataGenerators.PyData import PyData
from .StringBasic import StringBasic

class StringCategorical(StringBasic):
    """
    A base class for generating categorical string columns.
    Inherits from StringBasic and adds functionality for categorical columns.
    """
    def __init__(self, name:str, dataType:DataType=StringType(), nullalbe:bool=True, metadata:dict=None, column_values:list=None):
        """
        Initialize the column generator.

        Parameters:
        """
        super().__init__(name, dataType, nullalbe, metadata)
        self.column_values = column_values if column_values else metadata.get('column_values', None)
        if self.column_values is None:
            raise ValueError("For Categorical columns the column_values must be provided in metadata or as an argument column_values")

    @classmethod
    def create(cls, name:str, dataType:DataType=StringType(), nullalbe:bool=True, metadata:dict=None, **kwargs):
        """
        Create an instance of the column generator.

        Parameters:
        name (str): Name of the column.
        dataType (DataType): Data type of the column.
        nullalbe (bool): Whether the column can contain null values.
        metadata (dict): Metadata for the column.

        Returns:
        ColGenerator: An instance of the column generator.
        """
        # Try to create the string if there are no metadata requirements
        return cls(name, dataType, nullalbe, metadata, **kwargs)
    
    @classmethod
    def supports_requirements(cls, dataType:DataType=StringType(), nullalbe:bool=True, metadata:dict=None, **kwargs):
        """
        Check if the column generator supports the specified requirements.

        Parameters:
        dataType (DataType): Data type of the column.
        nullalbe (bool): Whether the column can contain null values.
        metadata (dict): Metadata for the column.

        Returns:
        bool: True if the requirements are supported, False otherwise.
        """
        metadata = {} if not metadata else metadata
        if type(dataType) in [StringType] and ('column_values' in metadata.keys() or 'column_values' in kwargs.keys()):
            return True
        return False

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

        li_indexes = PyData.random_ints(i_row_count, 0, len(self.column_values)-1)
        li_column = [self.column_values[i] for i in li_indexes]
        return li_column

    def set_metadata(self, metadata:dict):
        """
        Set the metadata for the column. Allow for overriding for complex col generators.

        Parameters:
        metadata (dict): Metadata for the column.
        """
        return super().set_metadata(metadata)

        