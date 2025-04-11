import pytest
from DataCreator.DataGenerators.FirstNameData import FirstNameData
from DataCreator.ColGenerators.StringFirstName import StringFirstName
from DataCreator.ColGenerators.StringBasic import StringBasic
from DataCreator.ColGenerators.ColGenerator import ColGenerator

class TestStringFirstName():

    @pytest.fixture(scope="class")
    def s_test_parquet_path(self):
         return r"F:\Spark_Data_Test\SSA_FirstNames_Stats"

    @pytest.fixture(scope="class")
    @pytest.mark.usefixtures("spark_session", "s_test_parquet_path")
    def create_first_name_data(self, spark_session, s_test_parquet_path):
        # Initialize the FirstNameData set (currently required to pass the spark session and file path)
        first_name_data = FirstNameData(spark=spark_session, s_file_path=s_test_parquet_path)

    @pytest.mark.usefixtures("create_first_name_data")
    def test_create_string_first_name(self):
        # settings for the test
        s_col_name = "FirstName"
        i_row_count = 100
        # Create an instance of StringFirstName
        string_first_name = StringFirstName(name=s_col_name)
        df_names = string_first_name.generate_column(i_row_count)
        # Check if the DataFrame has the expected number of rows and columns
        assert df_names.count() == i_row_count
        assert len(df_names.columns) == 1
        assert df_names.columns[0] == s_col_name

    @pytest.mark.usefixtures("create_first_name_data")
    def test_create_from_factory_String(self):
        # settings for the test
        s_col_name = "FirstName"
        i_row_count = 100
        # Create an instance of StringFirstName using the factory method
        string_first_name = StringBasic.create(name=s_col_name, metadata={"ColType": "FirstName"})
        df_names = string_first_name.generate_column(i_row_count)
        # Check if the DataFrame has the expected number of rows and columns
        assert type(string_first_name) == StringFirstName
        assert df_names.count() == i_row_count
        assert len(df_names.columns) == 1
        assert df_names.columns[0] == s_col_name
        
    @pytest.mark.usefixtures("create_first_name_data")
    def test_create_from_factory_Base(self):
        # settings for the test
        s_col_name = "FirstName"
        i_row_count = 100
        # Create an instance of StringFirstName using the factory method
        string_first_name = ColGenerator.create(name=s_col_name, metadata={"ColType": "FirstName"})
        df_names = string_first_name.generate_column(i_row_count)
        # Check if the DataFrame has the expected number of rows and columns
        assert type(string_first_name) == StringFirstName
        assert df_names.count() == i_row_count
        assert len(df_names.columns) == 1
        assert df_names.columns[0] == s_col_name