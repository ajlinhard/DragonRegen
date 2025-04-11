
from abc import ABC, abstractmethod
from pyspark.sql.types import *
from ..DataGenerators.PyData import PyData

class ColGenerator(ABC):
    """
    Abstract base class for generating columns in a DataFrame.
    """
    def __init__(self, name:str, dataType:DataType=StringType, nullalbe:bool=True, metadata:dict=None):
        """
        Initialize the column generator.

        Parameters:
        spark_session (SparkSession): The Spark session to use.
        schema (StructField): The schema for the column.
        """
        self.name = name
        self.dataType = dataType
        self.nullable = nullalbe
        self.metadata = metadata

    @classmethod
    @abstractmethod
    def create(cls, name:str, dataType:DataType=StringType, nullalbe:bool=True, metadata:dict=None, **kwargs):
        subclasses = cls.__subclasses__()
        ls_deprioritize = ["ColBasic"]
        for subclass in sorted(subclasses, key=lambda x: x.__name__ if x.__name__ not in ls_deprioritize else 'zzzzzz'):
            if hasattr(subclass, 'supports_requirements') :
                supported = subclass.supports_requirements(dataType, nullalbe, metadata, **kwargs)
                print(f"Checking subclass: {subclass.__name__} and requirements: {supported}")
                if supported:
                    return supported(name, dataType, nullalbe, metadata, **kwargs)
        raise ValueError(f"No suitable column generator found for {dataType} with nullable={nullalbe} and metadata={metadata}.")


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

    @classmethod
    @abstractmethod
    def supports_requirements(cls, dataType:DataType=StringType, nullalbe:bool=True, metadata:dict=None, **kwargs):
        """
        Check if the column generator supports the specified requirements.

        Parameters:
        dataType (DataType): Data type of the column.
        nullalbe (bool): Whether the column can contain null values.
        metadata (dict): Metadata for the column.

        Returns:
        bool: True if the requirements are supported, False otherwise.
        """
        return None

    @abstractmethod
    def generate_column(self, i_row_count: int) -> list:
        """
        Generate a column of data based on the specified schema.

        Parameters:
        num_rows (int): Number of rows to generate.
        schema (StructField): Schema for the column.

        Returns:
        list: Generated column data.
        """
        if isinstance(self.dataType, StringType):
            return PyData.random_strings(i_row_count, 1, 20)
        elif isinstance(self.dataType, IntegerType):
            return PyData.random_ints(i_row_count, 1, 100)
        elif isinstance(self.dataType, FloatType):
            return PyData.random_floats(i_row_count, 1.0, 100.0)
        elif isinstance(self.dataType, DateType):
            return PyData.random_dates(i_row_count, "2020-01-01", "2023-12-31", granualarity="day")
        elif isinstance(self.dataType, TimestampNTZType):
            return PyData.random_dates(i_row_count, "2020-01-01", "2023-12-31", granualarity="second")

    @abstractmethod
    def set_metadata(self, metadata:dict):
        """
        Set the metadata for the column. Allow for overriding for complex col generators.

        Parameters:
        metadata (dict): Metadata for the column.
        """
        self.metadata = metadata

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
        