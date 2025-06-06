
from datetime import datetime, timedelta
from src.AIGuardian.Tasks.Waiters.Waiter import Waiter

class TaskComplete(Waiter):
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

    def check_conditions(self, **kwargs):
        """
        This method should implement the logic to pause execution until the condition is met.
        """
        task_id = kwargs.get('task_id', None)
        if task_id == self.condition:
            self.wait_complete = True
            if self.all_conditions_met():
                return self.callback(task_id) if self.callback else None
        if self.has_timed_out():
            raise TimeoutError(f"Wait conditions have timed out after {self.timeout} seconds.")

    def all_conditions_met(self):
        """
        This method should check if the condition for resuming execution is met.
        """
        return self.wait_complete

    def has_timed_out(self):
        """
        Check if the wait has timed out.
        
        :return: True if the timeout has been reached, False otherwise.
        """
        return (datetime.now() - self.start_time) > timedelta(seconds=self.timeout)