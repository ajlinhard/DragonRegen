from pyspark.sql.types import *
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from .StringBasic import StringBasic
from ..DataGenerators.LastNameData import LastNameData
from ..DataGenerators.PyData import PyData

class StringLastName(StringBasic):
    """
    Generate a column of first names.
    """
    def __init__(self, name:str, dataType:DataType=StringType(), nullalbe:bool=True, metadata:dict=None):
        """
        Initialize the column generator.

        Parameters:
        name (str): Name of the column.
        dataType (DataType): Data type of the column.
        nullalbe (bool): Whether the column can contain null values.
        metadata (dict): Metadata for the column.
        """
        super().__init__(name, dataType, nullalbe, metadata)

    @classmethod
    def supports_requirements(cls, dataType = StringType(), nullalbe = True, metadata = None):
        b_result = False
        if metadata is None:
            return False
        if metadata.get("ColType") == "LastName":
            b_result = True
        return b_result
    
    def generate_column(self, i_row_count):
        """
        Gernerate first names based on the provided indexes.
        
        Args:
            name_indexes (list or DataFrame): List of indexes to select first names from the DataFrame.
        """
        data_last_name = LastNameData()
        spark = data_last_name.spark
        df_last_names = data_last_name.df_last_names
        #TODO: maybe move the DataFrame create out to SparkData class
        # Generate random indexes for first names
        li_name_lkp = PyData.random_ints(i_row_count, 1, data_last_name.profile_max)
        # Create a DataFrame with the random indexes
        schema = StructType([StructField('name_int', IntegerType(), False)])
        df_names_int = spark.createDataFrame(zip(li_name_lkp), schema)

        # Join DataFrame with the first names DataFrame to get the first names
        df_new_name_str = df_names_int.join(df_last_names
                                              , on= (df_names_int.name_int > df_last_names.profile_lower_bound) & (df_names_int.name_int <= df_last_names.profile_upper_bound)
                                              , how='left') \
                                              .select(df_last_names.last_name.alias(self.name)) # rename column to user input self.name
        return df_new_name_str
        
        

