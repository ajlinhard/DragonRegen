import random
import string
from datetime import datetime, timedelta, date, time

from .BasicDataGenerators import BasicDataGenerators

class PyDataGenerators():
    """
    The BasicTypes class provides static methods for generating random data of various basic types.
    It includes methods for generating random strings, integers, floats, and dates.
    """

    @staticmethod
    def random_strings(length:int, min_length, max_length, charset=None):
        # Use default charset if none provided
        if charset is None:
            charset = string.ascii_letters + string.digits

        # Generate a list of random strings
        ls_random_strings = []
        for _ in range(length):
            string_length = random.randint(min_length, max_length)
            ls_random_strings.append(''.join(random.choice(charset) for _ in range(string_length)))

        return ls_random_strings
    
    @staticmethod
    def random_ints(length:int, min_value:int, max_value:int):
        # Generate a list of random integers
        return [random.randint(min_value, max_value) for _ in range(length)]
    
    @staticmethod
    def random_floats(length:int, min_value:float, max_value:float):
        # Generate a list of random floats
        return [random.uniform(min_value, max_value) for _ in range(length)]
    
    @staticmethod
    def random_dates(length:int, start_date, end_date, granualarity:str='second'):
        # Generate a list of random dates
        start = datetime.strptime(start_date, '%Y-%m-%d') if type(start_date)== str else start_date
        end = datetime.strptime(end_date, '%Y-%m-%d') if type(end_date)== str else end_date
        i_granularity = 0
        if granualarity == 'day':
            i_granularity = 1
        elif granualarity == 'hour':
            i_granularity = 2
        elif granualarity == 'minute':
            i_granularity = 3
        elif granualarity == 'second':
            i_granularity = 4
        else:
            raise ValueError("Invalid granularity. Choose from 'day', 'hour', 'minute', or 'second'.")
        # Determine the maximum values for hour, minute, and second based on granularity
        max_hour = 23 if i_granularity >= 2 else 0
        max_minute = 59 if i_granularity >= 3 else 0
        max_second = 59 if i_granularity >= 4 else 0
        # Calculate the days difference between start and end dates to allow only 1 random number to be required for date.
        delta_days = (end - start).days
        if delta_days < 0:
            raise ValueError("Start date must be before end date.")
        
        ls_random_dates = []
        for _ in range(length):
            rand_date = start + timedelta(days=random.randint(0, delta_days))
            ls_random_dates.append(
                datetime.combine(rand_date, time(
                   random.randint(0, max_hour),
                   random.randint(0, max_minute),
                   random.randint(0, max_second))
                )
            )
        return ls_random_dates


        

        

