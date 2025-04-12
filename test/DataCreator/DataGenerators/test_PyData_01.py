import random
import pytest
from datetime import datetime, timedelta, date, time
from DataCreator.DataGenerators.PyData import PyData

class TestPyData:

    @pytest.mark.parametrize('length, min_length, max_length, charset', [
        (5, 1, 10, 'abcdefghijklmnopqrstuvwxyz'),
        (8, 5, 15, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'),
        (10, 10, 20, '0123456789'),
        (12, 8, 16, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'),
        (12, 8, 16, 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?@#$%^&*()_+[]{}|;:,.<>')
    ])
    def test_random_strings(self, length, min_length, max_length, charset):
        # Create an instance of PyData
        pydata = PyData()

        # Generate random strings
        random_strings = pydata.random_strings(length, min_length, max_length, charset)

        # Check the length of the generated strings
        assert len(random_strings) == length

        # Check if the generated strings are within the specified length range
        random_length = [len(s) for s in random_strings]
        i_min = min(random_length)
        i_max = max(random_length)
        assert i_min >= min_length and i_max <= max_length, f"The Generate Min Length: {i_min} and Max Length: {i_max} are not within the specified range of {min_length} to {max_length}"

        # Check if the generated strings contain only characters from the specified charset
        for string in random_strings:
            assert all(char in charset for char in string)
    
    @pytest.mark.parametrize('length, min_value, max_value', [
        (5, 1, 10),
        (8, 5, 15),
        (10, 10, 20),
        (1000, 8, 522)
    ])
    def test_random_ints(self, length, min_value, max_value):
        # Generate random integers
        random_ints = PyData.random_ints(length, min_value, max_value)

        # Check the length of the generated integers
        assert len(random_ints) == length

        # Check if the generated integers are within the specified range
        i_cnt = 0
        i_type = 0
        for i in random_ints:
            if not min_value <= i <= max_value:
                i_cnt+=1 
            if not isinstance(i, int):
                i_type+=1
        # Flag results if any of the integers are not within the specified range
        assert i_cnt == 0, f"The were {i_cnt} intergers outside the range of {min_value} to {max_value}"
        assert i_type == 0, f"The were {i_type} integers that were not of type int."
    
    @pytest.mark.parametrize('length, min_value, max_value', [
        (5, 1.0, 10.0),
        (8, 5.0, 15.0),
        (10, 10.0, 20.0),
        (1000, 0.0, 1.0)
    ])
    def test_random_floats(self, length, min_value, max_value):
        # Generate random integers
        random_floats = PyData.random_floats(length, min_value, max_value)

        # Check the length of the generated integers
        assert len(random_floats) == length

        # Check if the generated integers are within the specified range
        i_cnt = 0
        i_type = 0
        for i in random_floats:
            if not min_value <= i <= max_value:
                i_cnt+=1 
            if not isinstance(i, float):
                i_type+=1
            
        # Flag results if any of the integers are not within the specified range
        assert i_cnt == 0, f"The were {i_cnt} values outside the range of {min_value} to {max_value}"
        assert i_type == 0, f"The were {i_type} values that were not of type floats."

    @pytest.mark.parametrize('length', [
        (5),
        (8),
        (10),
        (1000)
    ])
    def test_random_boolean(self, length):
        # Generate random integers
        random_booleans = PyData.random_booleans(length)

        # Check the length of the generated integers
        assert len(random_booleans) == length

        # Check if the generated integers are within the specified range
        i_type = 0
        for i in random_booleans:
            if not isinstance(i, bool):
                i_type+=1
            
        # Flag results if any of the integers are not within the specified range
        assert i_type == 0, f"The were {i_type} values that were not of type bool."

    
    def test_random_dates(self):
        """Test the random_dates static method of the PyData class."""
        # Test with string dates
        start_date = "2023-01-01"
        end_date = "2023-01-10"
        length = 100
        upper_bound_date = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))

        # Test with 'day' granularity
        dates_day = PyData.random_dates(length, start_date, end_date, "day")
        assert len(dates_day) == length
        for date in dates_day:
            assert isinstance(date, datetime)
            assert datetime.strptime(start_date, '%Y-%m-%d') <= date < upper_bound_date
            assert date.hour == 0
            assert date.minute == 0
            assert date.second == 0
        
        # Test with 'hour' granularity
        dates_hour = PyData.random_dates(length, start_date, end_date, "hour")
        assert len(dates_hour) == length
        for date in dates_hour:
            assert isinstance(date, datetime)
            assert datetime.strptime(start_date, '%Y-%m-%d') <= date < upper_bound_date
            assert 0 <= date.hour <= 23
            assert date.minute == 0
            assert date.second == 0
        
        # Test with 'minute' granularity
        dates_minute = PyData.random_dates(length, start_date, end_date, "minute")
        assert len(dates_minute) == length
        for date in dates_minute:
            assert isinstance(date, datetime)
            assert datetime.strptime(start_date, '%Y-%m-%d') <= date < upper_bound_date
            assert 0 <= date.hour <= 23
            assert 0 <= date.minute <= 59
            assert date.second == 0
        
        # Test with 'second' granularity (default)
        dates_second = PyData.random_dates(length, start_date, end_date)
        assert len(dates_second) == length
        for date in dates_second:
            assert isinstance(date, datetime)
            assert datetime.strptime(start_date, '%Y-%m-%d') <= date <= upper_bound_date
            assert 0 <= date.hour <= 23
            assert 0 <= date.minute <= 59
            assert 0 <= date.second <= 59
        
        # Test with datetime objects instead of strings
        start_dt = datetime(2023, 1, 1)
        end_dt = datetime(2023, 1, 10)
        dates_with_dt = PyData.random_dates(length, start_dt, end_dt)
        assert len(dates_with_dt) == length
        for date in dates_with_dt:
            assert isinstance(date, datetime)
            assert start_dt <= date < (end_dt + timedelta(days=1))
        
        # Test with zero length
        zero_dates = PyData.random_dates(0, start_date, end_date)
        assert len(zero_dates) == 0
        
        # Test invalid granularity
        with pytest.raises(ValueError, match="Invalid granularity"):
            PyData.random_dates(length, start_date, end_date, "invalid")
        
        # Test end date before start date
        with pytest.raises(ValueError, match="Start date must be before end date"):
            PyData.random_dates(length, end_date, start_date)
        
        # Test same start and end date (edge case)
        same_date = "2023-01-01"
        dates_same = PyData.random_dates(length, same_date, same_date)
        assert len(dates_same) == length
        for date in dates_same:
            assert date.date() == datetime.strptime(same_date, '%Y-%m-%d').date()
        
        # Test with a random seed for reproducibility
        random.seed(42)
        dates_seed1 = PyData.random_dates(length, start_date, end_date)
        random.seed(42)
        dates_seed2 = PyData.random_dates(length, start_date, end_date)
        for i in range(length):
            assert dates_seed1[i] == dates_seed2[i]