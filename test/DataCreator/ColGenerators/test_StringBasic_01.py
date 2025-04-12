import pytest
from pyspark.sql.types import *
from DataCreator.ColGenerators.StringBasic import StringBasic
from DataCreator.ColGenerators.ColGenerator import ColGenerator
from DataGuardian.Column.Compare import Compare

class TestStringCategorical01:

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs, expected", [
        (StringType(), True, None, {}, StringBasic),
        (StringType(), False, {}, {}, StringBasic),
        (IntegerType, True, None, {'column_values': ['a', 'b', 'c']}, None),
    ])
    def test_supports_requirements(self, dataType, nullalbe, metadata, kwargs, expected):
        # Test the requirements of StringCategorical
        b_result = StringBasic.supports_requirements(dataType, nullalbe, metadata, **kwargs)
        assert b_result == expected

    @pytest.mark.parametrize("name, dataType, nullalbe, metadata, kwargs", [
        ('col_test_1', StringType(), True, {'description': 'Test Column 1 is a basic string with random characters.'}, {}),
        ('col_test 2', StringType(), False, None, {}),
        ('col_test_3', StringType(), True, {"description": "ID of the user", "stats":{"source": "generated", "unique": False, "min": None, "max": None}}, {}),
    ])
    def test_ColField(self, name, dataType, nullalbe, metadata, kwargs, equal_column_structure):
        # Test the ColField of StringBasic
        test_col = StringBasic(name, dataType, nullalbe, metadata)
        ColStructField = test_col.ColField
        CompStructField = StructField(name, dataType, nullalbe, metadata)
        equal_column_structure(ColStructField, CompStructField)
        
    def test_create_factory(self, equal_column_structure):
        test_col = ColGenerator.create('test_str', StringType())
        assert isinstance(test_col, StringBasic), "The created column is not of type StringBasic"
        ColStructField = test_col.ColField
        CompStructField = StructField('test_str', StringType())
        equal_column_structure(ColStructField, CompStructField)

    @pytest.mark.parametrize("name, dataType, nullalbe, metadata, kwargs", [
        ('col_test_1', StringType(), True, {'description': 'Test Column 1 is a basic string with random characters.'}, {}),
        ('col_test 2', StringType(), False, None, {}),
        ('col_test_3', StringType(), True, {"description": "ID of the user", "stats":{"source": "generated", "unique": False, "min": None, "max": None}}, {}),
    ])
    def test_generate_column(self, name, dataType, nullalbe, metadata, kwargs):
        # Test the generate method of StringBasic
        test_col = StringBasic(name, dataType, nullalbe, metadata, **kwargs)
        i_row_count = 100
        generated_data = test_col.generate_column(i_row_count)
        assert len(generated_data) == i_row_count, f"Generated data length {len(generated_data)} does not match expected {i_row_count}"
