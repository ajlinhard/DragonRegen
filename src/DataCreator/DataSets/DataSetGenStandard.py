
from pyspark.sql import SparkSession, Catalog
from pyspark.sql.types import StructType, StructField
from .DataSetGenerator import DataSetGenerator
from ..Columns.ColGenerator import ColGenerator

class DataSetGenStandard(DataSetGenerator):

    def __init__(self, sparkSession:SparkSession , schema, i_row_count:int):
        self.spark = sparkSession
        self.schema = schema
        self.i_row_count = i_row_count
        self.df_data = None

    @classmethod
    def replicate_data(cls, spark:SparkSession, df_template, i_row_count:int=-1):
        """
        This method will replicate the data of the template DataFrame to create a new DataFrame with the specified number of rows.
        """
        # TODO: Iterate over each column and build out better schema
        # Get the schema of the template DataFrame
        schema = df_template.schema

        if i_row_count == -1:
            # If no row count is specified, use the number of rows in the template DataFrame
            i_row_count = int(df_template.count() * 0.1)
            # floor of 1000 rows
            i_row_count = max(i_row_count, 1000)

        return cls(spark, schema, i_row_count)

    def gererate_data(self):
        """
        This method will generate the data based on the schema and row count submitted. Then
        the data will be added to a spark Dataframe.
        """
        # Look at each struct field in the schema and generate the data for that field
        for field in self.schema:
            # Generate the data for the field based on its type
            ColGenerator.replicate(field).generate_column(self.i_row_count)
