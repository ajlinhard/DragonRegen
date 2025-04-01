from pyspark.sql import SparkSession, Catalog
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from abc import ABC, abstractmethod

class DataSetGenerator(ABC):

    @abstractmethod
    def gererate_data(self):
        """
        This method will initiate the generation of the data for the data set.
        """
        pass