from abc import ABC, abstractmethod
import datetime
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
from src.AIGuardian.AIDataModels.AILogs import TaskLog, TaskCompleted
from src.AIGuardian.AIUtils.GenAIUtils import GenAIUtils
from src.AIGuardian.Tasks.TaskExceptions import ValidateAIResponseError
from src.MetaFort.AILoggingTopics import AILoggingTopics
from src.MetaFort.SysLogs.DatabaseEngine import DatabaseEngine
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine

class Task(ABC):

    def __init__(self, input_params={}, sequence_limit=10, verbose=False, parent_task=None):
        self.input_params = {} if input_params is None else input_params
        self.output_params = {}
        self.output_artifacts = []
        self.output_artifacts_pub_index = 0
        self.verbose = verbose
        self.parent_task = parent_task
        # Task tree variables and identifiers
        self.task_id = str(uuid.uuid4())
        self.group_task_id = self.task_id 
        self.sequence = 0
        self.sequence_limit = sequence_limit
        self._task_state = None
        self._task_state_code = 0
        self.is_completed = False
        self.user_prompt = None

        # read-only properties
        self._name = self.__class__.__name__
        self._description = Task.get_description() # self.description 
        self._task_type = Task.get_task_type()
        self._system_prompt = Task.get_system_prompt()
        self._task_version = Task.get_task_version()

        # TODO create wait objects? so we can wait for diff reasons.
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
    def get_description():
        return 'The base Task class. This should be inherited by all Task classes.'
    
    @staticmethod
    @abstractmethod
    def get_task_type():
        return 'base_Task'
    
    @staticmethod
    @abstractmethod
    def get_task_version():
        return '0.0.1'
    
    @staticmethod
    @abstractmethod
    def get_system_prompt():
        return """This is the system prompt for the base Task."""
    
    # endregion static variables

    # region Properties
    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description
        # return self.__class__.get_description()
    
    @property
    def task_type(self):
        return self._task_type
    
    @property
    def task_version(self):
        return self._task_version
    
    @property
    def task_state(self):
        return self._task_state
    
    @task_state.setter
    def task_state(self, value):
        self._set_task_state_code(value)
        self._task_state = value

    @task_version.setter
    def task_state(self, value):
        self._task_version = value

    def _set_task_state_code(self, task_state):
        """
        Set the task_state code based on the task_state string.
        """
        self._task_state_code = TaskState(task_state)

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
            "log_dt": datetime.datetime.now().isoformat(),
            "task_state": self.task_state,
            "error_code": error_code,
            "error_message": error_message,
            "error_timestamp": datetime.datetime.now().isoformat() if error_message else None,
            "metadata": json.dumps({"step_status": step_status}) if step_status else None,
        }
        return data_row
    
    def submit_task(self, user_prompt=None):
        """
        Get the Task ID.
        """
        # put or pull from the database
        self.input_params['user_prompt'] = user_prompt

        data_row = {"task_id": self.task_id,
            "task_name": self.name,
            "task_version": self.task_version,
            "parent_task_id": self.parent_task.task_id if self.parent_task else None,
            "group_task_id": self.group_task_id,
            "description": self.description,
            "sequence_number": self.sequence,
            "created_dt": datetime.datetime.now().isoformat(),
            "updated_dt": datetime.datetime.now().isoformat(),
            "input_artifacts": self.input_params,
            # "input_artifacts": json.dumps(self.input_params) if isinstance(self.input_params, dict) and self.input_params else None,
        }
        return TaskLog(**data_row)
    
    # endregion logging

    # region Setup Methods
    def initialize(self):
        """
        Initialize the Task with the necessary parameters.
        """
        self.setup_input_params()
        
    def setup_input_params(self):
        """
        Setup the input parameters for the Task. Sometimes it will be mined or pulled from parent Tasks.
        """
        # TODO: May want to add a list of parameters to pull from the parent Task.
        parent_task_params =  dict(**self.parent_task.input_params, **self.parent_task.output_params) if self.parent_task else {}
        self.input_params = self.input_params if self.input_params is not None else {}
        self.input_params = {**self.input_params, **parent_task_params}

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
            "insert_dt": datetime.datetime.now().isoformat(),
            "output_artifacts": self.output_params
        }
        self.output_artifacts.append(TaskCompleted(**data_row))

    def is_waiting(self):
        """
        Check if the Task is still waiting for dependencies.
        """
        return len(self.waiting_list) > 0

    def process_dependency_check(self, completed_tasks):
        """
        Check if the Task is still waiting for dependencies.
        """
        removed_child_tasks = []
        for task_json in completed_tasks:
            task_id = task_json.get("task_id")
            if task_id in self.waiting_list:
                print(f"==> Removing {task_id} from child tasks.")
                self.waiting_list.remove(task_id)
                self.waiting_list[task_id] = task_json.get("output_artifacts", None)
        return removed_child_tasks
    
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