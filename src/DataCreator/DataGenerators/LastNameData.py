import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from .FromDataSingleton import FromDataSingleton
from ..ConfigSys import ConfigSys

class LastNameData(metaclass=FromDataSingleton):
    """Singleton class for last name data.

    This class is a singleton that provides a list of last names.
    It is designed to be used as a singleton to ensure that the same instance is used throughout the application.
    """
    def __init__(self, spark:SparkSession, s_file_path:str=None, options:dict=None):
        """Initialize the LastNameData instance.

        Args:
            s_file_path (str, optional): Path to the file containing last names. Defaults to None.
        """
        self.spark = spark
        self.s_file_path = s_file_path if s_file_path else os.path.abspath(os.path.join(ConfigSys().data_path(),"census_surname_bounds.parquet"))
        self.options = options if options else {}
        self.df_last_names = None
        self.load_last_names()

    def load_last_names(self):
        """
        Load the last names from the passed file into a DataFrame for use by other generators.
        """
        self.df_last_names = self.spark.read.parquet(self.s_file_path+r'\*.parquet')
        # confirm columns are present
        if 'last_name' not in self.df_last_names.columns:
            raise ValueError("Column 'last_name' not found in the DataFrame.")
        if 'profile_lower_bound' not in self.df_last_names.columns:
            raise ValueError("Column 'profile_lower_bound' not found in the DataFrame.")
        if 'profile_upper_bound' not in self.df_last_names.columns:
            raise ValueError("Column 'profile_upper_bound' not found in the DataFrame.")
        
    # TODO: Option to load into memory/cache for speed.
    # TODO: Options to rename columns of input to match expected names.
    
    @property
    def profile_max(self):
        """
        Gernerate last names based on the provided indexes.
        
        Args:
            name_indexes (list or DataFrame): List of indexes to select last names from the DataFrame.
        """
        return self.df_last_names.select(max('profile_upper_bound')).collect()[0][0]