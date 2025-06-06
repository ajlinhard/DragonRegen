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
from src.AIGuardian.AIUtils.GenAIUtils import GenAIUtils
from src.AIGuardian.Tasks.TaskExceptions import ValidateAIResponseError
from src.AIGuardian.Tasks.Task import Task
from src.AIGuardian.AIDataModels.AILogs import TaskLog, TaskArtifact, LLMRequest
from src.MetaFort.AILoggingTopics import AILoggingTopics
from src.MetaFort.SysLogs.DatabaseEngine import DatabaseEngine
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine

class TaskAI(Task, ABC):

    def __init__(self, input_params={}, sequence_limit=10, verbose=False, parent_task=None):
        super().__init__(input_params=input_params, sequence_limit=sequence_limit, verbose=verbose, parent_task=parent_task)
        # override the Task class variables
        self.function_order = [self.initialize, self.engineer_prompt, self.generate_task, self.complete_task]
        # Task AI specific variables
        self.engineered_prompt = None
        self.text_response = None

        self.model_parameters = {"max_tokens": 10000,
            "temperature": 0.1,
            "stop_sequences": ["}"],
            "pref_model_type": "COMPLEX",
        }
        self.ai_client = None
 
    # region static variables
    @staticmethod
    @abstractmethod
    def get_description():
        return 'The base Task AI class, which adds prompting an LLM.'
    
    @staticmethod
    @abstractmethod
    def get_task_type():
        return 'TaskAI'
    
    @staticmethod
    @abstractmethod
    def get_system_prompt():
        return """This is the system prompt for the base Task."""
    
    # endregion static variables

    # region Setup Methods
    def initialize(self):
        """
        Initialize the Task with the necessary parameters.
        """
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

    # region Task AI Methods
    @abstractmethod
    def engineer_prompt(self, user_prompt=None):
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
    
    def complete_task(self):
        """
        Complete the Task based of the values from the AI gnerated response. Fill in the output_params for the Task.
        """
        # This method should be overridden in subclasses to provide specific completion Tasks
        # Write the message as a new TaskArtifact
        data_row = {
            "task_id": self.task_id,
            "group_task_id": self.group_task_id,
            "insert_dt": datetime.datetime.now().isoformat(),
            "name": 'LLM Response',
            "description": self.input_params.get("description", ""),
            "parts": [self.text_response],
            "metadata": self.model_parameters,
            "extensions": None   
        }
        self.output_artifacts.append(TaskArtifact(**data_row))
        self.is_completed = True
        return super().complete_task()
        
    def generate_task(self, retry_cnt=1, **kwargs):
        current_retry = 0
        # Set default values for parameters
        self.model_parameters.setdefault("model", "claude-3-7-sonnet-20250219")
        kwargs = dict(**kwargs, **self.model_parameters)
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
                    "request_parameters": {key: kwargs[key] for key in model_keys if key in kwargs},
                    "user_prompt": self.user_prompt,
                    "engineered_prompt": self.engineered_prompt,
                    "api_request_id": str(message._request_id),
                    "raw_response": message.content[0].text,
                    "parsed_results": text_response,
                    "response_metadata": json.dumps({"role": message.role, 
                                        "stop_sequence": message.stop_sequence, 
                                        "stop_reason": message.stop_reason, 
                                        "usage": vars(message.usage)}),
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                    "request_timestamp": request_timestamp.isoformat(),
                    "response_timestamp": response_timestamp.isoformat(),
                    "duration_ms": duration.total_seconds(),
                    "error_code":  str(type(log_error)) if log_error else None, #log_error.__class__.__name__
                    "error_message": str(log_error) if log_error else None,
                    "error_timestamp": datetime.datetime.now().isoformat() if log_error else None,
                    "retry_cnt": current_retry-1,
                    "RAG_Embeding_Model": None,
                    "RAG_IDs": None,
                    "RAG_Versions": None,
                    "metadata": None,
                }
                self.output_artifacts.append(LLMRequest(**data_row))
            #end while loop

    # endregion Task AI Methods
        