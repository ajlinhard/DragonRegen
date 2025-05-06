from abc import ABC, abstractmethod
import datetime
import json
from dotenv import load_dotenv
import anthropic

# Internal imports
from ..AIUtils.GenAIUtils import GenAIUtils
from ..Actions.ActionExceptions import ValidateAIResponseError
from ...MetaFort.AILoggingTables import AILoggingTables
from src.MetaFort.SysLogs.DatabaseEngine import DatabaseEngine

class Action(ABC):
    _registry = {}

    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_action=None):
        self.input_params = input_params
        self.output_params = None
        self.verbose = verbose
        # action tree variables and identifiers
        self.action_id = None
        self.group_action_id = None
        self.sequence = 0
        self.sequence_limit = sequence_limit
        self.user_prompt = None
        self.engineered_prompt = None
        self.response = None
        self.text_response = None
        self.parent_action = parent_action
        self.child_action = None
        # read-only properties
        self._name = self.__class__.__name__
        self._description = Action.get_description() # self.description 
        self._action_type = Action.get_action_type()
        self._action_version = Action.get_action_version()
        self._system_prompt = Action.get_system_prompt()
        self.model_parameters = {"max_tokens": 10000,
            "temperature": 0.1,
            "stop_sequences": ["}"],
            "pref_model_type": "COMPLEX",
            "ai_tools": self.get_tools(),
        }
        self._step_name = 'CREATED'
        self._step_name_code = 0
        self.is_completed = False
        ## Initialize the AI client
        self.ai_client = None
        self.db_engine = None

    @classmethod
    def register(cls, action_name):
        def decorator(subclass):
            cls._registry[action_name] = subclass
            return subclass
        return decorator

    @classmethod
    def from_parent_action(cls, parent_action):
        """
        Create a new action from a parent action.
        """
        new_action = cls(
            parent_action=parent_action,
        )
        new_action.initialize()
        return new_action

    # region static variables
    @staticmethod
    @abstractmethod
    def get_description():
        return 'The base action class. This should be inherited by all action classes.'
    
    @staticmethod
    @abstractmethod
    def get_action_type():
        return 'base_action'
    
    @staticmethod
    @abstractmethod
    def get_action_version():
        return '0.0.1'

    @staticmethod
    @abstractmethod
    def get_system_prompt():
        return """This is the system prompt for the base action."""
    
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
    def action_type(self):
        return self._action_type
    
    @property
    def action_version(self):
        return self._action_version
    
    @property
    def step_name(self):
        return self._step_name
    
    @step_name.setter
    def step_name(self, value):
        self._set_step_name_code(value)
        self._step_name = value

    def _set_step_name_code(self, step_name):
        """
        Set the step_name code based on the step_name string.
        """
        step_name_mapping = {
            "CREATED": 0,
            "INITIALIZED": 100,
            "PROCESSING": 300,
            "COMPLETED": 500,
            "FAILED": 900,
        }
        if step_name not in step_name_mapping:
            raise ValueError(f"Invalid step_name: {step_name}. Valid step_names are: {list(step_name_mapping.keys())}")
        self._step_name_code = step_name_mapping[step_name]

    def set_action_id(self, action_id=None):
        self.action_id = action_id
        if self.group_action_id is None:
                self.group_action_id = self.action_id

    # endregion Properties

    # region logging
    def start_action_id(self):
        """
        Get the action ID.
        """
        if self.action_id is None:
            # put or pull from the database
            table = AILoggingTables.AI_ACTION_LOG_TABLE
            data_row = {"action_name": self.name,
                "action_version": self.action_version,
                "parent_action_id": self.parent_action.action_id if self.parent_action else None,
                "group_action_id": self.group_action_id,
                "description": self.description,
                "sequence_number": self.sequence,
                "created_dt": datetime.datetime.now(),
                "updated_dt": datetime.datetime.now(),
                "step_status": 'SUCCESS',
                "step_name": self.step_name,
                "metadata": json.dumps(self.input_params) if isinstance(self.input_params, dict) and self.input_params else None,
            }
            action_id = self.db_engine.insert(table=table, data=data_row, output_data=['action_id'])[0][0]
            self.set_action_id(action_id=action_id)
            # db_engine.update(table=table, data={"updated_dt": datetime.datetime.now()}, where={"action_id": self.action_id})
        return action_id

    def update_action_id(self, step_name, step_status=None, error_code=None, error_message=None):
        """
        Update the action ID.
        """
        if self.action_id is not None:
            table = AILoggingTables.AI_ACTION_LOG_TABLE
            data_row = {
                "step_name": step_name,
                "step_status": step_status,
                "error_code": error_code,
                "error_message": error_message,
                "error_timestamp": datetime.datetime.now() if error_message else None,
                "updated_dt": datetime.datetime.now(),
            }
            self.db_engine.update(table=table, data=data_row, where={"action_id": self.action_id})
    
    def record_step(step_name):
        """
        Decorator to record the step of the action.
        """
        def record_decorator(func):
            def wrapper(self, *args, **kwargs):
                # Log the start of the step
                if step_name != 'INITIALIZED':
                    self.update_action_id(step_name=step_name, step_status='PROCESSING')
                # Call the original function
                result = func(self, *args, **kwargs)
                # Log the end of the step
                self.update_action_id(step_name=step_name, step_status='SUCCESS')
                if step_name:
                    self.step_name = step_name
                return result
            return wrapper
        return record_decorator
    
    # endregion logging

    # region Setup Methods
    @record_step('INITIALIZED')
    def initialize(self):
        """
        Initialize the action with the necessary parameters.
        """
        if self.parent_action is not None:
            self.group_action_id = self.parent_action.action_id
            self.group_action_id = self.parent_action.action_id
            self.sequence = self.parent_action.sequence + 1
            self.db_engine = self.parent_action.db_engine
            self.ai_client = self.parent_action.ai_client
        if self.db_engine is None:
            self.setup_db_engine()
        if self.ai_client is None:
            self.setup_client()
        self.setup_input_params()
        self.start_action_id()
        
    def setup_input_params(self):
        """
        Setup the input parameters for the action. Sometimes it will be mined or pulled from parent actions.
        """
        # TODO: May want to add a list of parameters to pull from the parent action.
        parent_action_params =  dict(**self.parent_action.input_params, **self.parent_action.output_params) if self.parent_action else {}
        self.input_params = self.input_params if self.input_params is not None else {}
        self.input_params = {**self.input_params, **parent_action_params}

    def setup_client(self):
        """
        Setup the AI client with the necessary parameters.
        """
        load_dotenv()
        self.ai_client = anthropic.Anthropic()

    def setup_db_engine(self):
        """
        Setup the database engine for logging.
        """
        # create database engine object and connection
        # driver = "ODBC Driver 17 for SQL Server"
        # server = 'localhost\\SQLEXPRESS' 
        # server = "Andrew=PC\\SQLEXPRESS"
        database = "MetaFort"
        # Server=localhost\SQLEXPRESS01;Database=master;Trusted_Connection=True;
        driver = "ODBC Driver 17 for SQL Server"
        server = 'localhost\\SQLEXPRESS' 

        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"Trusted_Connection=yes;"
        )
        db_engine = DatabaseEngine(conn_str)
        db_engine.connect()
        self.db_engine = db_engine

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

    # region Action Methods
    @abstractmethod
    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the action based on the user input.
        """
        # This method should be overridden in subclasses to provide specific prompts
        self.user_prompt = user_prompt
        self.engineered_prompt = user_prompt
        return self.engineered_prompt
    
    @abstractmethod
    def get_messages(self):
        """
        Get the messages for the action.
        """
        # This method should be overridden in subclasses to provide specific messages
        return [
            {"role": "user", "content": self.engineered_prompt},
        ]
    
    @abstractmethod
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the action.
        """
        # This method should be overridden in subclasses to provide specific validation
         # Reserved parameters for the actions
            # ai_tools -> used for feeding to the AI to potentially use.
            # rag_objects -> used for potentially pulling or pushing to the AI.
        return True
    
    @abstractmethod
    def hygiene_output(self, text_response):
        """
        Clean the output of the action.
        """
        # This method should be overridden in subclasses to provide specific cleaning
        return text_response
    
    @abstractmethod
    def validate_output(self, text_response):
        """
        Validate the output of the action.
        """
        # This method should be overridden in subclasses to provide specific validation
        self.text_response = text_response
        return True
    
    @record_step("COMPLETED")
    @abstractmethod
    def complete_action(self):
        """
        Complete the action based of the values from the AI gnerated response. Fill in the output_params for the action.
        """
        # This method should be overridden in subclasses to provide specific completion actions
        self.is_completed = True
        return self.output_params

    @abstractmethod
    def next_action(self):
        """
        Choose the next action based on the current action.
        """
        # This method should be overridden in subclasses to provide specific next actions
        self.child_action = [] if self.child_action is None else self.child_action
        return self.child_action
    
    def get_tools(self):
        """
        Get the tools for this action class or utility classes for the AI to consider using.
        """
        # This method should be overridden in subclasses to provide specific tools
        return None
    
    @record_step("PROCESSING")
    def generate_action(self, retry_cnt=1, **kwargs):
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
        table_name = AILoggingTables.AI_REQUEST_LOG_TABLE
        # Generate the JSON object using the AI client
        while(current_retry < retry_cnt):
            current_retry += 1
            # Send the request to the AI client
            request_timestamp = datetime.datetime.now()
            print(f"create_params: {create_params}")
            message = self.ai_client.messages.create(**create_params)
            response_timestamp = datetime.datetime.now()
            # Hygiene the output of the action
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
                    "action_id": self.action_id,
                    "insert_dt": datetime.datetime.now(),
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
                    "request_timestamp": request_timestamp,
                    "response_timestamp": response_timestamp,
                    "duration_ms": duration_ms,
                    "error_code":  str(type(log_error)) if log_error else None, #log_error.__class__.__name__
                    "error_message": str(log_error) if log_error else None,
                    "error_timestamp": datetime.datetime.now() if log_error else None,
                    "retry_cnt": current_retry-1,
                    "RAG_Embeding_Model": None,
                    "RAG_IDs": None,
                    "RAG_Versions": None,
                    "metadata": None,
                }
                self.db_engine.insert(table_name, data=data_row)
            #end while loop
        return message
    
    def run(self, user_prompt):
        """
        Run the action engine with the provided prompt.
        """
        if self._step_name_code < 100:
            self.initialize()
        # TODO: add a pre-engineer prompt step to extract parameters and validate.

        # Engineer the prompt based of the actions function
        prompt = self.engineer_prompt(user_prompt)

        # TODO: add a post-engineer prompt step to extract parameters
        # TODO: add an option to generate a think step-by-step option.

        # call the API
        # 1. The AI API will be called with the prompt, action settings
        # 2. Then use the validate_output method in the action class.
        # 3. If the output is valid, then log the action to the database.
        result = self.generate_action()
        self.response = result
        # Complete Action
        self.complete_action()
        
        for next_action in self.next_action():
            next_action.run(user_prompt=prompt)

        # endregion Action Methods