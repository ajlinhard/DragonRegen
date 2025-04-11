import pytest
from DataCreator.DataGenerators.FirstNameData import FirstNameData

class TestFirstNameData01():

    @pytest.fixture(scope="class")
    def s_test_parquet_path(self):
         return r"F:\Spark_Data_Test\census_firstname_bounds.parquet"

    @pytest.mark.usefixtures("spark_session","s_test_parquet_path", "cleanup_singleton")
    def test_Initialization(self, spark_session, s_test_parquet_path, cleanup_singleton):
        cleanup_singleton(FirstNameData)
        first_name_data = FirstNameData(spark=spark_session, s_file_path=s_test_parquet_path)
        assert first_name_data is not None, "FirstNameData instance should not be None"
        assert first_name_data.df_first_names is not None, "DataFrame should not be None"
        assert first_name_data.df_first_names.count() > 0, "DataFrame should not be empty"

    @pytest.mark.usefixtures("spark_session","s_test_parquet_path")
    def test_Singleton(self, spark_session, s_test_parquet_path):
        first_name_data1 = FirstNameData(spark=spark_session, s_file_path=s_test_parquet_path)
        first_name_data2 = FirstNameData()
        assert first_name_data1 is first_name_data2, "FirstNameData should be a singleton"
    
    @pytest.mark.usefixtures("spark_session","s_test_parquet_path")
    def test_Profile_Max(self, spark_session,s_test_parquet_path):
        first_name_data1 = FirstNameData(spark=spark_session, s_file_path=s_test_parquet_path)
        i_max = first_name_data1.profile_max
        assert i_max > 0, "Max profile should be greater than 0"
        assert i_max == 10_000_000, f"Max profile should be less than 10_000_000, but is {i_max:_} for file {s_test_parquet_path}"
        