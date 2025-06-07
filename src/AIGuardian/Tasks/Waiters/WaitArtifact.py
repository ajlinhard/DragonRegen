
from datetime import datetime, timedelta
from src.AIGuardian.Tasks.Waiters.Waiter import Waiter
from src.AIGuardian.AIDataModels.AILogs import TaskLog, TaskArtifact
from pydantic import BaseModel, Field

class WaitArtifact(Waiter):
    """
    WaitArtifact is a Waiter that pauses execution until a specific artifact is created by a task.
    """
    def __init__(self, condition:tuple, timeout=600, callback=None):
        """
        Initializes the Waiter with a condition.
        
        :param condition: A callable that returns True when the condition is met.
        """
        self.condition = condition # (task_id, artifact_name, artifact_model)
        self.wait_complete = False
        self.callback = callback
        self.timeout = timeout
        self.start_time = datetime.now()

    def check_conditions(self, dependency: BaseModel, **kwargs):
        """
        This method should implement the logic to pause execution until the condition is met.
        """
        if isinstance(dependency, TaskArtifact):
            if dependency.task_id == self.condition[0] and dependency.name == self.condition[1]:
                self.wait_complete = True
                if self.all_conditions_met():
                    self.callback(self, TaskArtifact) if self.callback else None
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