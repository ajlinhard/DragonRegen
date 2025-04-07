
from pyspark.sql.types import *
from ..DataGenerators.PyData import PyData
from .ColGenerator import ColGenerator

class StringBasic(ColGenerator):
    """
    Abstract base class for generating columns in a DataFrame.
    """
    def __init__(self, name:str, dataType:DataType=StringType(), nullalbe:bool=True, metadata:dict=None):
        """
        Initialize the column generator.

        Parameters:
        """
        super().__init__(name, dataType, nullalbe, metadata)

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
        if dataType in [StringType] and metadata is None and not kwargs:
            return cls(name, dataType, nullalbe, metadata)
        subclasses = cls.__subclasses__()
        for subclass in subclasses:
            if hasattr(subclass, 'supports_requirements') and subclass.supports_requirements(dataType, nullalbe, metadata, **kwargs):
                return subclass(name, dataType, nullalbe, metadata, **kwargs)
        # If no subclass supports the requirements, return the base class
        return cls(name, dataType, nullalbe, metadata)  
    
    @classmethod
    def supports_requirements(cls, dataType:DataType=StringType(), nullalbe:bool=True, metadata:dict=None):
        """
        Check if the column generator supports the specified requirements.

        Parameters:
        dataType (DataType): Data type of the column.
        nullalbe (bool): Whether the column can contain null values.
        metadata (dict): Metadata for the column.

        Returns:
        bool: True if the requirements are supported, False otherwise.
        """
        return type(dataType) in [StringType] and metadata is None

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
        