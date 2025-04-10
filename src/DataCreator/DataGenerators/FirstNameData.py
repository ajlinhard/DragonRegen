from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from .FromDataSingleton import FromDataSingleton

class FirstNameData(metaclass=FromDataSingleton):
    """Singleton class for first name data.

    This class is a singleton that provides a list of first names.
    It is designed to be used as a singleton to ensure that the same instance is used throughout the application.
    """
    def __init__(self, spark:SparkSession, s_file_path:str=None, options:dict=None):
        """Initialize the FirstNameData instance.

        Args:
            s_file_path (str, optional): Path to the file containing first names. Defaults to None.
        """
        self.spark = spark
        self.s_file_path = s_file_path if s_file_path else r"F:\Spark_Data_Test\census_firstname_bounds.parquet"
        self.options = options if options else {}
        self.df_first_names = None
        self.load_first_names()

    def load_first_names(self):
        """
        Load the first names from the passed file into a DataFrame for use by other generators.
        """
        self.df_first_names = self.spark.read.parquet(self.s_file_path)
        # confirm columns are present
        if 'first_name' not in self.df_first_names.columns:
            raise ValueError("Column 'first_name' not found in the DataFrame.")
        if 'profile_lower_bound' not in self.df_first_names.columns:
            raise ValueError("Column 'profile_lower_bound' not found in the DataFrame.")
        if 'profile_upper_bound' not in self.df_first_names.columns:
            raise ValueError("Column 'profile_upper_bound' not found in the DataFrame.")
        
    # TODO: Option to load into memory/cache for speed.
    # TODO: Options to rename columns of input to match expected names.
    
    @property
    def profile_max(self):
        """
        Gernerate first names based on the provided indexes.
        
        Args:
            name_indexes (list or DataFrame): List of indexes to select first names from the DataFrame.
        """
        return self.df_first_names.select(max(col('profile_upper_bound'))).collect()[0][0]