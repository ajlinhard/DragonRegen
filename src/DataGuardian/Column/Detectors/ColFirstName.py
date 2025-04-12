
from DataCreator.DataGenerators.FirstNameData import FirstNameData
from pyspark.sql import DataFrame
from DataGuardian.Column.Detectors.ColStats import ColStats

class ColFirstName(ColStats):
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

    def get_stats(self) -> DataFrame:
        base_stats = super().get_stats()
        # Get the first names DataFrame
        first_name_stats = self._type_stats()
        # Combine the base stats with the first name stats
        return {**base_stats, **first_name_stats}


    def _type_stats(self) -> bool:
        """
        Check if the column contains first names.
        """
        # TODO: Implement this function this is a placeholder of using RDD for efficency note
        df_base = self.df.alias("base")
        df_first_names = self.first_name_data.df_first_names.alias("first_names")
        # Join the DataFrames on the column and first name
        joined_df = df_base.join(df_first_names, df_base[self.column] == df_first_names["first_name"], "left") \
            .select(df_base[self.column], df_first_names["first_name"]).countif(df_first_names["first_name"].isNotNull())
        # Get the count of rows in the DataFrame
        total_count = self.df.count()
        first_name_count = joined_df.count()
        # Calculate the percentage of first names in the column

        return {"first_name_ratio": first_name_count * 1.0 / total_count if total_count > 0 else 0}

