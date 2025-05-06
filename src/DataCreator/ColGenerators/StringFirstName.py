from pyspark.sql.types import *
from pyspark.sql import DataFrame
from pyspark.sql.functions import *
from .StringBasic import StringBasic
from ..DataGenerators.FirstNameData import FirstNameData
from ..DataGenerators.PyData import PyData
from ..ColGenerators.ColGenRegistry import ColGenResistry

@ColGenResistry.add_registry("StringFirstName")
class StringFirstName(StringBasic):
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
    def supports_requirements(cls, dataType = StringType(), nullalbe = True, metadata = None, **kwargs):
        if metadata is None or type(StringType()) != StringType:
            return None
        if metadata.get("ColType") == "FirstName":
            return cls
        return None
     
     # region static variables for AI Guardian
    @staticmethod
    def get_description() -> str:
        """
        Get the description of the column generator.

        Returns:
        str: Description of the column generator.
        """
        return "A column that stores the first name of a person."
    
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
    
    def generate_column(self, i_row_count):
        """
        Gernerate first names based on the provided indexes.
        
        Args:
            name_indexes (list or DataFrame): List of indexes to select first names from the DataFrame.
        """
        null_ratio = self.metadata.get('stats',{}).get('null_ratio', 0.0)
        data_first_name = FirstNameData()
        spark = data_first_name.spark
        df_first_names = data_first_name.df_first_names
        #TODO: maybe move the DataFrame create out to SparkData class
        # Generate random indexes for first names
        li_name_lkp = PyData.random_ints(i_row_count, 1, data_first_name.profile_max, null_ratio)
        # Create a DataFrame with the random indexes
        schema = StructType([StructField('name_int', IntegerType(), False)])
        df_names_int = spark.createDataFrame(zip(li_name_lkp), schema)

        # Join DataFrame with the first names DataFrame to get the first names
        df_new_name_str = df_names_int.join(df_first_names
                                              , on= (df_names_int.name_int > df_first_names.profile_lower_bound) & (df_names_int.name_int <= df_first_names.profile_upper_bound)
                                              , how='left') \
                                              .select(df_first_names.first_name.alias(self.name)) # rename column to user input self.name
        return df_new_name_str.agg(collect_list("first_name").alias("list_column")).collect()[0]["list_column"]
        
        

