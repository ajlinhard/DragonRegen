import random
import string
import numpy as np
from .BasicData import BasicData

class NumPyData(BasicData):
    """
    The BasicTypes class provides static methods for generating random data of various basic types.
    It includes methods for generating random strings, integers, floats, and dates.
    """

    @staticmethod
    def random_strings(length:int, min_length, max_length, charset=None):
        """
        Generate a list of random strings of specified lengths.
        If no charset is provided, it defaults to alphanumeric characters.
        """
        if charset is None:
            charset = string.ascii_letters + string.digits
        
        # Generate random lengths for each string
        lengths = np.random.randint(min_length, max_length + 1, length)
        
        # Create a list to hold all strings
        result = []
        
        # For each desired length, generate a string of that length
        for l in lengths:
            # Generate indices into the charset
            char_indices = np.random.randint(0, len(charset), size=l)
            # Convert indices to characters and join
            random_str = ''.join(charset[i] for i in char_indices)
            result.append(random_str)
            
        return result
        
    @staticmethod
    def random_ints(length:int, min_value:int, max_value:int):
        # Generate a list of random integers
        pass