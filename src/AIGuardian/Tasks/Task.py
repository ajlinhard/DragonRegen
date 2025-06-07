from abc import ABC, abstractmethod
from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Dict, Any
from  datetime import datetime
import json
import uuid
from dotenv import load_dotenv
from anthropic import Anthropic, AsyncAnthropic
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskState,
)

# Internal imports
from src.AIGuardian.AIDataModels.AILogs import TaskCompleted
from src.AIGuardian.Tasks.Waiters.WaitTaskComplete import WaitTaskComplete
from src.AIGuardian.Tasks.Waiters.WaitArtifact import WaitArtifact
from src.AIGuardian.AIUtils.GenAIUtils import GenAIUtils
from src.AIGuardian.Tasks.TaskExceptions import ValidateAIResponseError
from src.MetaFort.AILoggingTopics import AILoggingTopics
from src.MetaFort.SysLogs.DatabaseEngine import DatabaseEngine
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine

class Task(ABC):
    task_id: str = Field(default=str(uuid.uuid4()), description="Primary key, unique identifier for the task")
    task_name: str = Field(..., description="Name of the task")
    parent_task_id: Optional[str] = None
    group_task_id: Optional[str] = None
    sequence: int = Field(default=0, description="Order of execution within the parent task")
    task_state: TaskState = Field(default=TaskState.submitted, description="Current state of the task")
    created_dt: datetime = Field(default=datetime.now(), description="Timestamp when the task was created")
    updated_dt: datetime = Field(default=datetime.now(), description="Timestamp when the task was last updated")
    input_artifacts: Dict[str, Any] = Field(default_factory=dict, description="Input artifacts for the task, can be parameters or data")
    waiting_list: List[WaitTaskComplete] = Field(default_factory=list, description="List of tasks that are waiting for this task to complete")

    def __init__(self, sequence_limit=10, verbose=False, parent_task=None, **data):
        super().__init__(**data)
        self.output_params = {}
        self.output_artifacts = []
        self.output_artifacts_pub_index = 0
        self.verbose = verbose
        self.parent_task = parent_task
        # Task tree variables and identifiers
        self.group_task_id = self.task_id 
        self.sequence_limit = sequence_limit
        self.is_completed = False
        self.user_prompt = None

        # processing list and function order
        self.waiting_list = []
        self.function_order = [self.initialize, self.complete_task]
        self.function_order_index = 0

        ## Initialize off parents
        if self.parent_task is not None:
            self.group_task_id = self.parent_task.group_task_id
            self.sequence = self.parent_task.sequence + 1
            self.ai_client = self.parent_task.ai_client
 
    # region static variables
    
    @staticmethod
    @abstractmethod
    def get_system_prompt():
        return """This is the system prompt for the base Task."""
    
    # endregion static variables

    # region Properties
    @computed_field
    @property
    def name(self):
        return self.__class__.__name__
    
    @computed_field
    @property
    def description(self):
        return 'The base Task class. This should be inherited by all Task classes.'
    
    @computed_field
    @property
    def task_type(self):
        return 'Base'
    
    @computed_field
    @property
    def task_version(self):
        return '0.0.1'
    
    # endregion Properties

    # region logging
    def update_task_log(self, task_state, step_status=None, error_code=None, error_message=None):
        """
        Update the Task ID.
        """
        data_row = {
            "task_log_id": uuid.uuid4().int,
            "task_id": self.task_id,
            "task_name": self.name,
            "group_task_id": self.group_task_id,
            "log_dt": datetime.now().isoformat(),
            "task_state": self.task_state,
            "error_code": error_code,
            "error_message": error_message,
            "error_timestamp": datetime.now().isoformat() if error_message else None,
            "metadata": json.dumps({"step_status": step_status}) if step_status else None,
        }
        return data_row
    
    # endregion logging

    # region Setup Methods
    def initialize(self):
        """
        Initialize the Task with the necessary parameters.
        """
        self.setup_input_artifacts()
        
    def setup_input_artifacts(self):
        """
        Setup the input parameters for the Task. Sometimes it will be mined or pulled from parent Tasks.
        """
        # TODO: May want to add a list of parameters to pull from the parent Task.
        parent_task_params =  dict(**self.parent_task.input_artifacts, **self.parent_task.output_params) if self.parent_task else {}
        self.input_artifacts = self.input_artifacts if self.input_artifacts is not None else {}
        self.input_artifacts = {**self.input_artifacts, **parent_task_params}

    def publish_artifacts(self):
        """
        Publish any new artifacts generated by the Task.
        """
        publish_list = self.output_artifacts[self.output_artifacts_pub_index:]
        self.output_artifacts_pub_index = len(self.output_artifacts) - 1
        return publish_list

    @abstractmethod
    def complete_task(self):
        """
        Complete the Task based of the values from the AI gnerated response. Fill in the output_params for the Task.
        """
        # This method should be overridden in subclasses to provide specific completion Tasks
        self.is_completed = True
        data_row = {
            "task_id": self.task_id,
            "task_name": self.name,
            "group_task_id": self.group_task_id,
            "insert_dt": datetime.now().isoformat(),
            "output_artifacts": self.output_params
        }
        self.output_artifacts.append(TaskCompleted(**data_row))

    def is_waiting(self):
        """
        Check if the Task is still waiting for dependencies.
        """
        return len(self.waiting_list) > 0
    
    def remove_wait(self, waiter):
        """
        The Base callback function for calling the waiters. 
        """
        if waiter not in self.waiting_list:
            raise ValueError(f"Waiter {waiter} not found in waiting list.")
        self.waiting_list.remove(waiter)

    def check_dependency(self, dependency):
        """
        Check if the Task is still waiting for dependencies.
        """
        for waiter in self.waiting_list:
            waiter.check_condition(dependency)

    def run(self, user_prompt=None):
        """
        Run the Task engine with the provided prompt.
        """
        while self.function_order_index < len(self.function_order):
            if self.is_waiting():
                return
            function = self.function_order[self.function_order_index]
            try:
                function()
                self.function_order_index += 1
            except Exception as e:
                print(f"==> Error running function {function.__name__}: {e}")
                self.task_state = TaskState.failed
                raise e
            # Check if after the function call if the task is now waiting
            if self.is_waiting():
                return
        # Add a backstop to ensure the task is completed
        if not self.is_completed:
            self.complete_task()
            
        # endregion Task Methods