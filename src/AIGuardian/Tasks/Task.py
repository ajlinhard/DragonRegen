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
from ..AIUtils.GenAIUtils import GenAIUtils
from .TaskExceptions import ValidateAIResponseError
from ...MetaFort.AILoggingTopics import AILoggingTopics
from src.MetaFort.SysLogs.DatabaseEngine import DatabaseEngine
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine

class Task(ABC):

    def __init__(self, input_params={}, sequence_limit=10, verbose=False, parent_task=None):
        self.input_params = {} if input_params is None else input_params
        self.output_params = {}
        self.verbose = verbose
        # Task tree variables and identifiers
        self.task_id = str(uuid.uuid4())
        self.group_task_id = self.task_id 
        self.sequence = 0
        self.sequence_limit = sequence_limit
        self.user_prompt = None
        self.engineered_prompt = None
        self.response = None
        self.text_response = None
        self.parent_task = parent_task
        self.child_task = []
        self.child_task_output_artifacts = {}
        self.processed_comp_tasks = []
        self.removed_comp_tasks = []
        # read-only properties
        self._name = self.__class__.__name__
        self._description = Task.get_description() # self.description 
        self._task_type = Task.get_task_type()
        self._task_version = Task.get_task_version()
        self._system_prompt = Task.get_system_prompt()
        self.model_parameters = {"max_tokens": 10000,
            "temperature": 0.1,
            "stop_sequences": ["}"],
            "pref_model_type": "COMPLEX",
            "ai_tools": self.get_tools(),
        }
        self._task_state = None
        self._task_state_code = 0
        self.is_completed = False
        ## Initialize the AI client
        self.ai_client = None
        self.db_engine = None
        if self.parent_task is not None:
            self.group_task_id = self.parent_task.group_task_id
            self.sequence = self.parent_task.sequence + 1
            self.db_engine = self.parent_task.db_engine
            self.ai_client = self.parent_task.ai_client
 
    @classmethod
    def from_parent_task(cls, parent_task):
        """
        Create a new Task from a parent Task.
        """
        new_Task = cls(
            parent_task=parent_task,
        )
        new_Task.initialize()
        return new_Task

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

    def set_task_id(self, task_id=None):
        self.task_id = task_id
        if self.group_task_id is None:
                self.group_task_id = self.task_id

    # endregion Properties

    # region logging
    def update_task(self, task_state, step_status=None, error_code=None, error_message=None):
        """
        Update the Task ID.
        """
        table = AILoggingTopics.AI_TASK_LOG_TOPIC
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
        if isinstance(self.db_engine, KafkaEngine):
            self.db_engine.insert(topic=table, data=data_row)
        else:
            self.db_engine.update(table=table, data=data_row, where={"task_id": self.task_id})
    
    def record_step(task_state):
        """
        Decorator to record the step of the Task.
        """
        def record_decorator(func):
            def wrapper(self, *args, **kwargs):
                # Log the start of the step
                func_name = func.__name__
                self.update_task(task_state=task_state, step_status=f'{func_name} - PROCESSING')
                try:
                    # Call the original function
                    result = func(self, *args, **kwargs)
                    # Log the end of the step
                    self.update_task(task_state=task_state, step_status=f'{func_name} - SUCCESS')
                except Exception as e:
                    # Log the error
                    self._set_task_state_code('failed')
                    self.update_task(task_state=task_state, step_status=f'{func_name} - FAILED', error_code=str(type(e)), error_message=str(e))
                    raise e
                return result
            return wrapper
        return record_decorator
    
    @record_step(TaskState.submitted)
    def submit_task(self, user_prompt=None):
        """
        Get the Task ID.
        """
        # put or pull from the database
        table = AILoggingTopics.AI_TASK_TOPIC
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
            "input_artifacts": json.dumps(self.input_params) if isinstance(self.input_params, dict) and self.input_params else None,
        }
        if isinstance(self.db_engine, KafkaEngine):
            self.db_engine.insert(topic=table, data=data_row)
        else:
            self.db_engine.insert(table=table, data=data_row)
        return data_row
    
    # endregion logging

    # region Setup Methods
    def initialize(self):
        """
        Initialize the Task with the necessary parameters.
        """
        if self.db_engine is None:
            self.setup_db_engine()
        if self.ai_client is None:
            self.setup_client()
        self.setup_input_params()
        
    def setup_input_params(self):
        """
        Setup the input parameters for the Task. Sometimes it will be mined or pulled from parent Tasks.
        """
        # TODO: May want to add a list of parameters to pull from the parent Task.
        parent_task_params =  dict(**self.parent_task.input_params, **self.parent_task.output_params) if self.parent_task else {}
        self.input_params = self.input_params if self.input_params is not None else {}
        self.input_params = {**self.input_params, **parent_task_params}

    def setup_client(self):
        """
        Setup the AI client with the necessary parameters.
        """
        load_dotenv()
        self.ai_client = Anthropic()
        # self.ai_client = AsyncAnthropic()

    def setup_db_engine(self):
        """
        Setup the database engine for logging.
        """
        self.db_engine = DatabaseEngine.default_builder()
        self.db_engine.connect()

    @abstractmethod
    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return {
            "output_type": GenAIUtils.valid_output_type("Text"),
            "output_struct": None,
        }

    # region Task Methods
    @abstractmethod
    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the Task based on the user input.
        """
        # This method should be overridden in subclasses to provide specific prompts
        self.user_prompt = user_prompt
        self.engineered_prompt = user_prompt
        return self.engineered_prompt
    
    @abstractmethod
    def get_messages(self):
        """
        Get the messages for the Task.
        """
        # This method should be overridden in subclasses to provide specific messages
        return [
            {"role": "user", "content": self.engineered_prompt},
        ]
    
    @abstractmethod
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the Task.
        """
        # This method should be overridden in subclasses to provide specific validation
         # Reserved parameters for the Tasks
            # ai_tools -> used for feeding to the AI to potentially use.
            # rag_objects -> used for potentially pulling or pushing to the AI.
        return True
    
    @abstractmethod
    def hygiene_output(self, text_response):
        """
        Clean the output of the Task.
        """
        # This method should be overridden in subclasses to provide specific cleaning
        return text_response
    
    @abstractmethod
    def validate_output(self, text_response):
        """
        Validate the output of the Task.
        """
        # This method should be overridden in subclasses to provide specific validation
        self.text_response = text_response
        return True
    
    @abstractmethod
    def complete_task(self):
        """
        Complete the Task based of the values from the AI gnerated response. Fill in the output_params for the Task.
        """
        # This method should be overridden in subclasses to provide specific completion Tasks
        self.is_completed = True
        print(f"==> Task {self.task_id} complete_task")
        self.db_engine.insert(
            topic=AILoggingTopics.AI_TASK_COMPLETED_TOPIC,
            data={
                "task_id": self.task_id,
                "task_name": self.name,
                "group_task_id": self.group_task_id,
                "insert_dt": datetime.datetime.now().isoformat(),
                "output_artifacts": json.dumps(self.output_params),
            }
        )
        return self.output_params

    @abstractmethod
    @record_step(TaskState.input_required)
    def wait_on_dependency(self, timeout=300):
        """
        Wait for the Task to complete before proceeding.
        """
        # This method should look at the completed topic for finished tasks or failed tasks.
        start_time = datetime.datetime.now()
        print(f"==> Waiting on {self.child_task} to complete.")
        while self.child_task and (datetime.datetime.now() - start_time).total_seconds() < timeout:
            completed_tasks = self.db_engine.consumers[AILoggingTopics.AI_TASK_COMPLETED_TOPIC].poll(timeout_ms=1000, max_records=10)
            self.wait_on_dependency_check(completed_tasks)

    def is_waiting(self):
        """
        Check if the Task is still waiting for dependencies.
        """
        return len(self.child_task) > 0

    def wait_on_dependency_check(self, completed_tasks):
        for topic_partition, messages in completed_tasks.items():
            for message in messages:
                if not isinstance(message.value, dict):
                    task_json = json.loads(message.value.decode('utf-8'))
                else:
                    task_json = message.value
                task_id = task_json.get("task_id")
                self.processed_comp_tasks.append(task_id)
                if task_id in self.child_task:
                    print(f"==> Removing {task_id} from child tasks.")
                    self.removed_comp_tasks.append(task_id)
                    self.child_task.remove(task_id)
                    self.child_task_output_artifacts[task_id] = task_json.get("output_artifacts", None)
        
        return self.is_waiting()
        
    def get_tools(self):
        """
        Get the tools for this task class or utility classes for the AI to consider using.
        """
        # This method should be overridden in subclasses to provide specific tools
        return []
    
    def generate_task(self, retry_cnt=1, **kwargs):
        current_retry = 0
        # Set default values for parameters
        kwargs = dict(**kwargs, **self.model_parameters)
        kwargs.setdefault("model", "claude-3-7-sonnet-20250219")
        kwargs.setdefault("max_tokens", 2000)
        kwargs.setdefault("temperature", 0.1)
        kwargs.setdefault("stop_sequences", ["}"])
        kwargs["messages"] = self.get_messages()
        create_func_params = ["model", "messages", "max_tokens", "temperature", "stop_sequences"]
        model_keys = ["model", "max_tokens", "temperature", "stop_sequences"]
        
        message = None
        # subset kwargs to only include model keys
        create_params = {key: kwargs[key] for key in kwargs.keys() if key in create_func_params}
        table_name = AILoggingTopics.AI_REQUEST_LOG_TOPIC
        # Generate the JSON object using the AI client
        while(current_retry < retry_cnt):
            current_retry += 1
            # Send the request to the AI client
            request_timestamp = datetime.datetime.now()
            message = self.ai_client.messages.create(**create_params)
            response_timestamp = datetime.datetime.now()
            # Hygiene the output of the Task
            text_response = message.content[0].text
            text_response = self.hygiene_output(text_response)
            # Set logging parameters
            duration = (response_timestamp - request_timestamp)
            duration_ms = (duration.total_seconds() * 1000) + duration.microseconds

            # Check if the response is valid JSON
            log_error = None
            try:
                if self.validate_output(text_response):
                    self.text_response = text_response
                    break  # Exit the loop if JSON is valid
            # Only retry if the error is a validation error
            except ValidateAIResponseError as e:
                log_error = e
                if self.verbose:
                    print(f"Error message: {str(e)}")
                # If this is the last retry, raise the error
                if current_retry >= retry_cnt:
                    raise e
            except Exception as e:
                log_error = e
                if self.verbose:
                    print(f"Error message: {str(e)}")
                # Always raise non-validation errors
                raise e
            finally:
                # TODO: may need to handle if message is None
                # Log the response to the database
                data_row = {
                    "task_id": self.task_id,
                    "insert_dt": datetime.datetime.now().isoformat(),
                    "status": "SUCCESS" if log_error is None else "FAILED",
                    "ai_service": "Anthropic",
                    "model": kwargs["model"],
                    "request_parameters": json.dumps({key: kwargs[key] for key in model_keys if key in kwargs}),
                    "user_prompt": self.user_prompt,
                    "engineered_prompt": self.engineered_prompt,
                    "api_request_id": str(message._request_id),
                    "raw_response": message.content[0].text,
                    "parsed_results": text_response,
                    "response_metadate": json.dumps({"role": message.role, 
                                        "stop_sequence": message.stop_sequence, 
                                        "stop_reason": message.stop_reason, 
                                        "usage": vars(message.usage)}),
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                    "request_timestamp": request_timestamp.isoformat(),
                    "response_timestamp": response_timestamp.isoformat(),
                    "duration_ms": duration_ms,
                    "error_code":  str(type(log_error)) if log_error else None, #log_error.__class__.__name__
                    "error_message": str(log_error) if log_error else None,
                    "error_timestamp": datetime.datetime.now().isoformat() if log_error else None,
                    "retry_cnt": current_retry-1,
                    "RAG_Embeding_Model": None,
                    "RAG_IDs": None,
                    "RAG_Versions": None,
                    "metadata": None,
                }
                self.db_engine.insert(table_name, data=data_row)
            #end while loop
        return message
    
    def run(self, user_prompt=None, delay_waiting=False):
        """
        Run the Task engine with the provided prompt.
        """
        if self._task_state != TaskState.working or self.ai_client is None:
            self.initialize()
        # TODO: add a pre-engineer prompt step to extract parameters and validate.
        # Engineer the prompt based of the Tasks function
        if user_prompt is None or user_prompt == "":
            user_prompt = self.input_params.get("user_prompt", None)
        print(f"==> Running {self.name} with prompt: {user_prompt}")
        prompt = self.engineer_prompt(user_prompt)

        # TODO: add a post-engineer prompt step to extract parameters
        # TODO: add an option to generate a think step-by-step option.

        # call the API
        # 1. The AI API will be called with the prompt, Task settings
        # 2. Then use the validate_output method in the Task class.
        # 3. If the output is valid, then log the Task to the database.
        result = self.generate_task()
        self.response = result
        if not delay_waiting:
            # Wait on dependencies
            if self.child_task:
                self.wait_on_dependency()
            # Complete Task
            self.complete_task()
        
        # endregion Task Methods