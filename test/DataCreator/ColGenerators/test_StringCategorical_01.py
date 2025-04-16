import pytest
from pyspark.sql.types import *
from DataCreator.ColGenerators.Categorical import Categorical
from DataCreator.ColGenerators.ColGenerator import ColGenerator
from DataGuardian.Column.Compare import Compare

class TestCategorical01:

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs, expected", [
        (StringType(), True, None, {'column_values': ['a', 'b', 'c']}, Categorical),
        (StringType(), True, None, {}, None),
        (StringType(), False, {'column_values': ['a', 'b', 'c']}, {}, Categorical),
        (IntegerType(), True, None, {'column_values': ['a', 'b', 'c']}, None),
    ])
    def test_supports_requirements(self, dataType, nullalbe, metadata, kwargs, expected):
        # Test the requirements of Categorical
        b_result = Categorical.supports_requirements(dataType, nullalbe, metadata, **kwargs)
        assert b_result == expected

    def test_create_factory(self, equal_column_structure):
        test_col = ColGenerator.create('test_str', StringType(), metadata={'column_values': ['N/a', 'invalid', 'valid']})
        assert isinstance(test_col, Categorical), "The created column is not of type Categorical"
        ColStructField = test_col.ColField
        CompStructField = StructField('test_str', StringType(), metadata={'column_values': ['N/a', 'invalid', 'valid']})
        equal_column_structure(ColStructField, CompStructField)

    @pytest.mark.parametrize("name, dataType, nullalbe, metadata, kwargs", [
        ('col_test_1', StringType(), True, None, {'column_values': ['a', 'b', 'c']}),
        ('col_test 2', StringType(), False, {'column_values': ['a', 'b', 'c']}, {}),
        ('col_test_3', StringType(), True, {"description": "ID of the user", "stats":{"source": "generated", "unique": True, "min": 1, "max": None}}, {'column_values': ['a', 'b', 'c']}),
    ])
    def test_ColField(self, name, dataType, nullalbe, metadata, kwargs, equal_column_structure):
        # Test the ColField of Categorical
        test_col = Categorical(name, dataType, nullalbe, metadata, **kwargs)
        ColStructField = test_col.ColField
        CompStructField = StructField(name, dataType, nullalbe, metadata)
        equal_column_structure(ColStructField, CompStructField)

    @pytest.mark.parametrize("name, dataType, nullalbe, metadata, kwargs", [
        ('col_test_1', StringType(), True, None, {'column_values': ['a', 'b', 'c']}),
        ('col_test 2', StringType(), False, {'column_values': ['a', 'b', 'c']}, {}),
        ('col_test_3', StringType(), True, {"description": "ID of the user", "stats":{"source": "generated", "unique": True, "min": 1, "max": None}}, {'column_values': ['a', 'b', 'c']}),
    ])
    def test_generate_column(self, name, dataType, nullalbe, metadata, kwargs):
        # Test the generate method of StringBasic
        test_col = Categorical(name, dataType, nullalbe, metadata, **kwargs)
        i_row_count = 100
        # Pull Values from generated data
        generated_data = test_col.generate_column(i_row_count)
        set_generated_data = set(generated_data)
        # Pull expected input values from metadata or kwargs (using sets to make categorical distinct values quickly)
        metadata = {} if not metadata else metadata
        set_parameter_data = set(metadata.get('column_values', kwargs.get('column_values')))

        # Check results
        assert len(generated_data) == i_row_count, f"Generated data length {len(generated_data)} does not match expected {i_row_count}"
        assert len(set_generated_data.difference(set_parameter_data)) == 0, f"Generated data {set_generated_data} does not match parameter data {set_parameter_data}"