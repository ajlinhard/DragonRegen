
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class Waiter(ABC):
    """
    Abstract base class for Waiters.
    Waiters are used to pause execution until a certain condition is met.
    """
    def __init__(self, condition=None, timeout=600, callback=None):
        """
        Initializes the Waiter with a condition.
        
        :param condition: A callable that returns True when the condition is met.
        """
        self.condition = condition
        self.wait_complete = False
        self.callback = callback
        self.timeout = timeout
        self.start_time = datetime.now()

    @abstractmethod
    def check_conditions(self, **kwargs):
        """
        This method should implement the logic to pause execution until the condition is met.
        """
        pass

    @abstractmethod
    def all_conditions_met(self):
        """
        This method should check if the condition for resuming execution is met.
        """
        pass

    @abstractmethod
    def has_timed_out(self):
        """
        Check if the wait has timed out.
        
        :return: True if the timeout has been reached, False otherwise.
        """
        if self.wait_complete:
            return True
        return (datetime.now() - self.start_time) > timedelta(seconds=self.timeout)