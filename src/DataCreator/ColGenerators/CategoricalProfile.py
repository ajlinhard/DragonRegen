
from pyspark.sql.types import *
from .Categorical import Categorical
from ..DataGenerators import PyData

class CategoricalProfile(Categorical):

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
        if ('column_values_ratio' in metadata.keys() or 'column_values_ratio' in kwargs.keys()):
            return cls
        print('Nothing found')
        return None

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
        column_values_ratio = list(self.metadata.get('stats',{}).get('column_values_ratio',[]))
        if len(column_values_ratio) != len(self.column_values):
            raise ValueError('The column_values_ratio is not the same length as the column_values! They must be equivalent for the generation to work')
        li_ratios = PyData.random_floats(i_row_count, 0.0, 1.0, null_ratio)
        # TODO Make Numpy instead
        li_column = []
        for val in li_ratios:
            for i, r in zip(range(0, len(column_values_ratio)), column_values_ratio):
                if val < r:
                    li_column.append(self.column_values[i])

        return li_column