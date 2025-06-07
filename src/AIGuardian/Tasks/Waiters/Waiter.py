
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from typing import Callable, Any

class Waiter(ABC, BaseModel):
    """
    Abstract base class for Waiters.
    Waiters are used to pause execution until a certain condition is met.
    """
    condition: Any = Field(..., description="A callable that returns True when the condition is met.")
    callable: Callable = Field(..., description="A callback function to be executed when the condition is met.")
    timeout: int = Field(default=600, description="Maximum time to wait for the condition to be met, in seconds.")
    start_time: datetime = Field(default_factory=datetime.now, description="Timestamp when the waiter was initialized.")

    def __init__(self, **data):
        """
        Initializes the Waiter with a condition.
        
        :param condition: A callable that returns True when the condition is met.
        """
        super().__init__(**data)
        self.wait_complete = False

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