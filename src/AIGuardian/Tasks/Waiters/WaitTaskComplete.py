
from datetime import datetime, timedelta
from pydantic import BaseModel
from src.AIGuardian.Tasks.Waiters.Waiter import Waiter
from src.AIGuardian.AIDataModels.AILogs import TaskLog, TaskCompleted 

class WaitTaskComplete(Waiter):
    """
    Abstract base class for Waiters.
    Waiters are used to pause execution until a certain condition is met.
    """
    def __init__(self, condition: str, timeout=600, callback=None):
        """
        Initializes the Waiter with a condition.
        
        :param condition: A callable that returns True when the condition is met.
        """
        self.condition = condition
        self.wait_complete = False
        self.callback = callback
        self.timeout = timeout
        self.start_time = datetime.now()

    def check_conditions(self, dependency: BaseModel, **kwargs):
        """
        This method should implement the logic to pause execution until the condition is met.
        """
        if isinstance(dependency, TaskCompleted):
            if dependency.task_id == self.condition:
                self.wait_complete = True
                if self.all_conditions_met():
                    self.callback(self) if self.callback else None
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
        return super().has_timed_out()