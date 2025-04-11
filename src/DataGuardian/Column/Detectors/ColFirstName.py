
from DataCreator.DataGenerators.FirstNameData import FirstNameData
from pyspark.sql import DataFrame

class FirstName():
    """
    This Class will provide a rating of the likelihood that a column contains first names.
    It will use the FirstNameData class to load a DataFrame of first names and their bounds.
    The threshold will be set to a default, but will pass meta data back with the score. Additionally, the
    inclusion of null values in the score will be toggled by the user.
    """
    def __init__(self, df: DataFrame, column: str, b_include_nulls: bool = False):
        self.df = df
        self.column = column
        self.first_name_data = FirstNameData()

    def is_first_name(self) -> bool:
        """
        Check if the column contains first names.
        """
        # TODO: Implement this function this is a placeholder of using RDD for efficency note
        # Check if the column exists in the DataFrame
        if self.column not in self.df.columns:
            raise ValueError(f"Column {self.column} does not exist in the DataFrame.")

        # Get the first few values from the column
        sample_values = self.df.select(self.column).limit(10).rdd.flatMap(lambda x: x).collect()

        # Check if any of the sample values are first names
        for value in sample_values:
            if not self.first_name_data.is_first_name(value):
                return False

        return True
