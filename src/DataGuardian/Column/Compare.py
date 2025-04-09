from pyspark.sql.types import *

class Compare:

    @staticmethod
    def equal_structure(col1: StructField, col2: StructField, ignore_name: bool = False):
        """
        Fixture to create a DataFrame with equal column structure.
        """
        assert type(col1) == StructField
        assert type(col2) == StructField
        assert col1.dataType == col2.dataType
        if not ignore_name:
            assert col1.name == col2.name
        assert col1.nullable == col2.nullable
        assert col1.metadata == col2.metadata