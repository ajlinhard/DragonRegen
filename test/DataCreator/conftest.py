from pyspark.sql import SparkSession
import pytest

@pytest.fixture(scope="module")
def spark_session():
    """
    Fixture to create a Spark session for testing.
    """
    spark = SparkSession.builder \
        .appName("TestSession") \
        .master("local[*]") \
        .getOrCreate()

    yield spark

    spark.stop()