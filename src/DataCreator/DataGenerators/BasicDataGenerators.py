import random
import string
from abc import ABC, abstractmethod

class BasicDataGenerators(ABC):
    """
    The BasicTypes class provides static methods for generating random data of various basic types.
    It includes methods for generating random strings, integers, floats, and dates.
    """

    @staticmethod
    @abstractmethod
    def random_strings(length:int, min_length, max_length, charset=None):
        """G
        Generate a list of random strings of specified lengths.
        If no charset is provided, it defaults to alphanumeric characters.
        """
        pass
    
    @staticmethod
    @abstractmethod
    def random_ints(length:int, min_value:int, max_value:int):
        # Generate a list of random integers
        pass