
from pyspark.sql.types import *
from ..DataGenerators.PyData import PyData
from .ColGenerator import ColGenerator

class Categorical(ColGenerator):
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
        # Check Data Type and values the same
        d_types = {}
        for i in self.column_values:
            s_type = str(type(i))
            if s_type in d_types.keys():
                d_types[s_type] += d_types.get(s_type, 0) + 1
            else:
                d_types[s_type] = 1

        # Ignore NoneType since it is null
        # d_types.pop(type(None))
        if len(d_types) > 1:
            raise Exception(f'The column_values for the Categorical ColType are not all the same data type! There data is {d_types}')
        # TODO make this error check work d_type[0] does not work
        # if not isinstance(Categorical.map_to_dataType(d_types[0]), dataType):
        #     raise Exception(f'The column_values are {d_types[0]}, but the passed dataType is {dataType}')

    @staticmethod
    def map_to_dataType(s_type):
        if s_type is int():
            return IntegerType()
        elif s_type is str():
            return StringType()
        return None

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
        if not metadata and not kwargs:
            print('no meta')
            return None
        metadata = {} if not metadata else metadata
        if ('column_values' in metadata.keys() or 'column_values' in kwargs.keys()):
            # TODO add this as teh abstract classes code the call super() via self. or cls.
            subclasses = cls.__subclasses__()
            for subclass in subclasses:
                if hasattr(subclass, 'supports_requirements'):
                    supported = subclass.supports_requirements(dataType, nullalbe, metadata, **kwargs)
                    if supported:
                        return supported
            return cls
        print('Nothing found')
        return None

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
        null_ratio = self.metadata.get('stats',{}).get('null_ratio', 0.0)
        li_indexes = PyData.random_ints(i_row_count, 0, len(self.column_values)-1, null_ratio)
        li_column = [None if i is None else self.column_values[i] for i in li_indexes]
        return li_column

    def set_metadata(self, metadata:dict):
        """
        Set the metadata for the column. Allow for overriding for complex col generators.

        Parameters:
        metadata (dict): Metadata for the column.
        """
        return super().set_metadata(metadata)

        