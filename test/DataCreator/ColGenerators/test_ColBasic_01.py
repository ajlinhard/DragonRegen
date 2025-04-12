import pytest
from pyspark.sql.types import *
from DataCreator.ColGenerators.ColBasic import ColBasic
from DataCreator.ColGenerators.ColGenerator import ColGenerator
from DataGuardian.Column.Compare import Compare

class TestColBasic():
    """
    Test class for ColBasic generator.
    """

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs, expected", [
        (DataType(), True, None, {}, ColBasic),
        (FloatType(), False, {}, {}, ColBasic),
        (IntegerType(), False, {}, {}, ColBasic),
        (DoubleType(), True, None, {}, ColBasic),
        (BooleanType(), True, None, {}, ColBasic),
        (StringType(), True, None, {'column_values': ['a', 'b', 'c']}, ColBasic),
        (ArrayType(IntegerType()), True, None, {}, None),
    ])
    def test_supports_requirements(self, dataType, nullalbe, metadata, kwargs, expected):
        # Test the requirements of StringCategorical
        b_result = ColBasic.supports_requirements(dataType, nullalbe, metadata)
        assert b_result == expected

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs", [
        (DataType(), True, None, {}),
        (FloatType(), False, {}, {}),
        (IntegerType(), False, {}, {}),
        (DoubleType(), True, None, {}),
        (BooleanType(), True, None, {}),
        (StringType(), True, None, {'column_values': ['a', 'b', 'c']}),
        (ArrayType(IntegerType()), True, None, {}),
    ])
    def test_supports_requirements(self, dataType, nullalbe, metadata, kwargs, equal_column_structure):
        # Test the initialization of ColBasic
        col_name =  'test_str'
        col_basic = ColBasic(col_name, dataType, nullalbe, metadata)
        assert isinstance(col_basic, ColBasic)
        ColStructField = col_basic.ColField
        CompStructField = StructField(col_name, dataType, nullalbe, metadata)
        equal_column_structure(ColStructField, CompStructField)

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs", [
        (DateType(), True, None, {}),
        (FloatType(), False, {}, {}),
        (IntegerType(), False, {}, {}),
        (DoubleType(), True, None, {}),
        (BooleanType(), True, None, {}),
        (StringType(), True, None, {'column_values': ['a', 'b', 'c']}),
    ])
    def test_generate_column(self, dataType, nullalbe, metadata, kwargs):
        # Test the generate method of StringBasic
        name = 'test_col'
        test_col = ColBasic(name, dataType, nullalbe, metadata, **kwargs)
        i_row_count = 100
        generated_data = test_col.generate_column(i_row_count)
        assert len(generated_data) == i_row_count, f"Generated data length {len(generated_data)} does not match expected {i_row_count}"

    @pytest.mark.parametrize("dataType, nullalbe, metadata, kwargs", [
        (ArrayType(IntegerType()), True, None, {}),
    ])
    def test_generate_column_unsupported(self, dataType, nullalbe, metadata, kwargs):
        # Test the generate method of StringBasic
        name = 'test_col'
        with pytest.raises(ValueError): 
            test_col = ColBasic(name, dataType, nullalbe, metadata, **kwargs)
            i_row_count = 100
            generated_data = test_col.generate_column(i_row_count)

    def test_replicate(self):
        test_StringType = StructField("name", IntegerType(), True)
        test_StrinCol = ColBasic.replicate(test_StringType)
        ls_str = test_StrinCol.generate_column(100)
        for i in ls_str:
            assert isinstance(i, int), f"Expected string, got {type(i)}"
      