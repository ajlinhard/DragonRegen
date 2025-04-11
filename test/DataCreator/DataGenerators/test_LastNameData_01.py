import pytest
from DataCreator.DataGenerators.LastNameData import LastNameData

class TestLastNameData01():

    @pytest.fixture(scope="class")
    def s_test_parquet_path(self):
         return r"F:\Spark_Data_Test\census_surname_bounds.parquet"

    @pytest.mark.usefixtures("spark_session","s_test_parquet_path", "cleanup_singleton")
    def test_Initialization(self, spark_session, s_test_parquet_path, cleanup_singleton):
        cleanup_singleton(LastNameData)
        last_name_data = LastNameData(spark=spark_session, s_file_path=s_test_parquet_path)
        assert last_name_data is not None, "LastNameData instance should not be None"
        assert last_name_data.df_last_names is not None, "DataFrame should not be None"
        assert last_name_data.df_last_names.count() > 0, "DataFrame should not be empty"

    @pytest.mark.usefixtures("spark_session","s_test_parquet_path")
    def test_Singleton(self, spark_session, s_test_parquet_path):
        last_name_data1 = LastNameData(spark=spark_session, s_file_path=s_test_parquet_path)
        last_name_data2 = LastNameData()
        assert last_name_data1 is last_name_data2, "LastNameData should be a singleton"
    
    @pytest.mark.usefixtures("spark_session","s_test_parquet_path")
    def test_Profile_Max(self, spark_session,s_test_parquet_path):
        last_name_data1 = LastNameData(spark=spark_session, s_file_path=s_test_parquet_path)
        i_max = last_name_data1.profile_max
        assert i_max > 0, "Max profile should be greater than 0"
        assert i_max == 10_000_000, f"Max profile should be less than 10_000_000, but is {i_max:_} for file {s_test_parquet_path}"
        