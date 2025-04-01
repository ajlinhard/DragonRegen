import random
import string
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StringType, IntegerType
from .BasicDataGenerators import BasicDataGenerators

class SparkDataGenerators(BasicDataGenerators):
    """
    The BasicTypes class provides static methods for generating random data of various basic types.
    It includes methods for generating random strings, integers, floats, and dates.
    """

    @staticmethod
    def random_strings(length:int, min_length, max_length, charset=None):
        """
        Generate a list of random strings of specified lengths.
        If no charset is provided, it defaults to alphanumeric characters.
        """
        if charset is None:
            charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

        func_string = F.udf(lambda x: ''.join(random.choice(charset) for _ in range(x)))
        # Function to create a random character from our character set
        # First, generate a random length for each row
        df = df.withColumn("string_length", 
                        (F.rand() * (max_length - min_length + 1) + min_length).cast(IntegerType()))

        df = df.withColumn("random_string",func_string(F.col("string_length")))

    @staticmethod
    def random_ints(length:int, min_value:int, max_value:int):
        # Generate a list of random integers
        df = spark.range(0, length)
        return df.withColumn("random_int", (F.rand() * 100).cast(IntegerType()))  # Random int between 0 and 100
