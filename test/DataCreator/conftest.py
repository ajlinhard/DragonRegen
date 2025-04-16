from pyspark.sql import SparkSession
from pyspark.sql.types import *
import pytest
from DataGuardian.Column.Compare import Compare

@pytest.fixture(scope="module")
def spark_session():
    """
    Fixture to create a Spark session for testing.
    """
    spark = SparkSession.builder \
        .appName("TestSession") \
        .enableHiveSupport() \
        .master("local[*]") \
        .getOrCreate()

    yield spark

    spark.stop()

@pytest.fixture(scope="function")
def equal_column_structure():
    """
    Fixture to create a DataFrame with equal column structure.
    """
    return Compare.equal_structure
