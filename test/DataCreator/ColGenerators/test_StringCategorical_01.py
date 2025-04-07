import pytest
from pyspark.sql.types import *
from DataCreator.ColGenerators.StringCategorical import StringCategorical

class TestStringCategorical01:

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs, expected", [
        (StringType(), True, None, {'column_values': ['a', 'b', 'c']}, True),
        (StringType(), True, None, {}, False),
        (StringType(), False, {'column_values': ['a', 'b', 'c']}, {}, True),
        (IntegerType(), True, None, {'column_values': ['a', 'b', 'c']}, False),
    ])
    def test_supports_requirements(self, dataType, nullalbe, metadata, kwargs, expected):
        # Test the requirements of StringCategorical
        b_result = StringCategorical.supports_requirements(dataType, nullalbe, metadata, **kwargs)
        assert b_result == expected