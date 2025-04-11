import pytest
from pyspark.sql.types import *
from DataCreator.ColGenerators.StringCategorical import StringCategorical
from DataGuardian.Column.Compare import Compare

class TestStringCategorical01:

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs, expected", [
        (StringType(), True, None, {'column_values': ['a', 'b', 'c']}, StringCategorical),
        (StringType(), True, None, {}, None),
        (StringType(), False, {'column_values': ['a', 'b', 'c']}, {}, StringCategorical),
        (IntegerType(), True, None, {'column_values': ['a', 'b', 'c']}, None),
    ])
    def test_supports_requirements(self, dataType, nullalbe, metadata, kwargs, expected):
        # Test the requirements of StringCategorical
        b_result = StringCategorical.supports_requirements(dataType, nullalbe, metadata, **kwargs)
        assert b_result == expected

    @pytest.mark.parametrize("name, dataType, nullalbe, metadata, kwargs", [
        ('col_test_1', StringType(), True, None, {'column_values': ['a', 'b', 'c']}),
        ('col_test 2', StringType(), False, {'column_values': ['a', 'b', 'c']}, {}),
    ])
    def test_ColField(self, name, dataType, nullalbe, metadata, kwargs, equal_column_structure):
        # Test the ColField of StringCategorical
        test_col = StringCategorical(name, dataType, nullalbe, metadata, **kwargs)
        ColStructField = test_col.ColField
        CompStructField = StructField(name, dataType, nullalbe, metadata)
        equal_column_structure(ColStructField, CompStructField)

