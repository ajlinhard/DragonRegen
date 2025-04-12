from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import *
from pyspark.sql.types import *

class ColStats():

    def __init__(self, spark: SparkSession, df: DataFrame, col_name: str, sample_percent: float = 0.1):
        self.spark = spark
        self.df = df
        self.col_name = col_name
        # Check if the column exists in the DataFrame
        if self.col_name not in self.df.columns:
            raise ValueError(f"Column '{self.col_name}' does not exist in the DataFrame.")
        self.sample_percent = sample_percent

    def get_stats(self) -> DataFrame:
        """
        Get column statistics for the specified column in the DataFrame. We are going to take advantage of
        the lazy compiling of Spark SQL to build the query and avoid processing until all states are ready.
        """
        df_col_stats = self.get_sample()
        df_col_stats = self.df.agg(
            count(when(col(self.col_name).isNotNull(), 1)).alias("count_pop"),
            count().alias("count"),
            min(col(self.col_name)).alias("min_Val"),
            max(col(self.col_name)).alias("max_Val"),
            countDistinct(col(self.col_name)).alias("count_distinct")
        )
        
        if self.df.schema[self.col_name].dataType in [IntegerType(), FloatType(), DoubleType()]:
            df_col_stats = df_col_stats.agg(
                mean(col(self.col_name)).alias("mean"),
                sum(when(col(self.col_name).isNotNull(), col(self.col_name))).alias("sum"),
                stddev_pop(col(self.col_name)).alias("stddev_pop"),
            )

        # Get column statistics
        d_stats = self.df.select('*').collect()[0].asDict()
        return d_stats
    
    def get_sample(self) -> DataFrame:
        """
        Get a sample of the DataFrame based on the specified sample percentage.
        """
        if self.sample_percent is None or self.sample_percent == 1.0:
            return self.df
        return self.df.sample(fraction=self.sample_percent, seed=42)
    
