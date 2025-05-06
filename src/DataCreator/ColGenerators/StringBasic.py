
from pyspark.sql.types import *
from ..DataGenerators.PyData import PyData
from .ColGenerator import ColGenerator
from ..ColGenerators.ColGenRegistry import ColGenRegistry

@ColGenRegistry.add_registry("StringBasic")
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
        if type(dataType) in [StringType] and metadata is None and not kwargs:
            return cls(name, dataType, nullalbe, metadata)
        # Check if any subclass supports the requirements
        subclasses = cls.__subclasses__()
        ls_deprioritize = [] # Here for future mechanism to deprioritize certain classes
        for subclass in sorted(subclasses, key=lambda x: x.__name__ if x.__name__ not in ls_deprioritize else 'zzzzzz'):
            if hasattr(subclass, 'supports_requirements') :
                supported = subclass.supports_requirements(dataType, nullalbe, metadata, **kwargs)
                print(f"Checking subclass: {subclass.__name__} and requirements: {supported}")
                if supported:
                    return supported(name, dataType, nullalbe, metadata, **kwargs)
        # If no subclass supports the requirements, return the base class
        return cls(name, dataType, nullalbe, metadata)  
    
    @classmethod
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
        if type(dataType) != StringType:
            return None
        elif type(dataType) in [StringType] and metadata is None:
            return cls
        else:
            subclasses = cls.__subclasses__()
            for subclass in subclasses:
                if hasattr(subclass, 'supports_requirements'):
                    supported = subclass.supports_requirements(dataType, nullalbe, metadata, **kwargs)
                    if supported:
                        return supported
        return cls

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
    
     
     # region static variables for AI Guardian
    @staticmethod
    def get_description() -> str:
        """
        Get the description of the column generator.

        Returns:
        str: Description of the column generator.
        """
        return "This is a basic string column generator that can be used to generate a column of strings with a specified length and format. It is not intended for free text or complex string generation."
    
    @staticmethod
    def get_metadata_json() -> dict:
        """
        Get the metadata JSON for the column generator.

        Returns:
        dict: Metadata JSON for the column generator.
        """
        return {
                "description": "Place the description of the column here.",
                "unique_fl": True,
                "default_value": None
            }
    
    @staticmethod
    def get_examples() -> str:
        """
        Get the examples for the column generator.

        Returns:
        str: Examples for the column generator.
        """
        return """Example 1:
        Purpose: "This table is used to store user information."
        Column Info: "user_id": "unique ID representing each user."
        Output:
        <JSON_Template>
        {"name": "user_id", "type": "Integer", "nullable": False, 
            "metadata": {"description": "unique ID representing each user.", 
            "unique_fl": True,
            "default_value": None}}
        </JSON_Template>"""
    # endregion static variables for AI Guardian

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

        