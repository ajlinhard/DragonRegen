import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from DataCreator.DataSets.DataSetGenStandard import DataSetGenStandard

class TestBasicCreate():

    @pytest.mark.usefixtures("spark_session")
    def test_create_simple_df(self, spark_session):
        # Create a DataSetGenStandard object
        testSchema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("city", StringType(), True)
        ])

        data_gen = DataSetGenStandard(spark_session, testSchema, 100)
        # Generate the DataFrame
        df = data_gen.generate_data()
        assert df.columns == ["id", "name", "age", "city"]

    @pytest.mark.usefixtures("spark_session")
    def test_base_datat_types(self, spark_session):
        # Create a DataSetGenStandard object
        test_count = 1755
        testSchema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("city", StringType(), True),
            StructField("salary", FloatType(), True),
            StructField("transaction_date", DateType(), True),
            StructField("insert_datetime", TimestampNTZType(), True),
            StructField("update_datetime", TimestampNTZType(), True),
        ])
        data_gen_all_types = DataSetGenStandard(spark_session, testSchema, test_count)
        # Generate the DataFrame
        df_all_types = data_gen_all_types.generate_data()
        assert df_all_types.count() == test_count
        assert df_all_types.columns == ["id", "name", "age", "city", "salary", "transaction_date", "insert_datetime", "update_datetime"]
        assert df_all_types.dtypes == [('id', 'int'),
            ('name', 'string'),
            ('age', 'int'),
            ('city', 'string'),
            ('salary', 'float'),
            ('transaction_date', 'date'),
            ('insert_datetime', 'timestamp_ntz'),
            ('update_datetime', 'timestamp_ntz')]
