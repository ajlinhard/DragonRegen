import pytest
from DataCreator.DataGenerators.LastNameData import LastNameData
from DataCreator.ColGenerators.StringLastName import StringLastName
from DataCreator.ColGenerators.StringBasic import StringBasic
from DataCreator.ColGenerators.ColGenerator import ColGenerator

class TestStringLastName():

    @pytest.fixture(scope="class")
    def s_test_parquet_path(self):
         return r"F:\Spark_Data_Test\census_surname_bounds.parquet"

    @pytest.fixture(scope="class")
    @pytest.mark.usefixtures("spark_session", "s_test_parquet_path")
    def create_last_name_data(self, spark_session, s_test_parquet_path):
        # Initialize the LastNameData set (currently required to pass the spark session and file path)
        last_name_data = LastNameData(spark=spark_session, s_file_path=s_test_parquet_path)

    @pytest.mark.usefixtures("create_last_name_data")
    def test_create_string_last_name(self):
        # settings for the test
        s_col_name = "LastName"
        i_row_count = 100
        # Create an instance of StringLastName
        string_last_name = StringLastName(name=s_col_name)
        df_names = string_last_name.generate_column(i_row_count)
        # Check if the DataFrame has the expected number of rows and columns
        assert df_names.count() == i_row_count
        assert len(df_names.columns) == 1
        assert df_names.columns[0] == s_col_name

    @pytest.mark.usefixtures("create_last_name_data")
    def test_create_from_factory_String(self):
        # settings for the test
        s_col_name = "LastName"
        i_row_count = 100
        # Create an instance of StringLastName using the factory method
        string_last_name = StringBasic.create(name=s_col_name, metadata={"ColType": "LastName"})
        df_names = string_last_name.generate_column(i_row_count)
        # Check if the DataFrame has the expected number of rows and columns
        assert type(string_last_name) == StringLastName
        assert df_names.count() == i_row_count
        assert len(df_names.columns) == 1
        assert df_names.columns[0] == s_col_name
        
    @pytest.mark.usefixtures("create_last_name_data")
    def test_create_from_factory_Base(self):
        # settings for the test
        s_col_name = "LastName"
        i_row_count = 100
        # Create an instance of StringLastName using the factory method
        string_last_name = ColGenerator.create(name=s_col_name, metadata={"ColType": "LastName"})
        df_names = string_last_name.generate_column(i_row_count)
        # Check if the DataFrame has the expected number of rows and columns
        assert type(string_last_name) == StringLastName
        assert df_names.count() == i_row_count
        assert len(df_names.columns) == 1
        assert df_names.columns[0] == s_col_name