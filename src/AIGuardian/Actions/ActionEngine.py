from abc import ABC, abstractmethod
from dotenv import load_dotenv
import anthropic
import datetime
import json

# Internal imports
from ..Actions.ActionExceptions import ValidateAIResponseError
from ...MetaFort.AILoggingTables import AILoggingTables

class ActionEngine():
    def __init__(self, action, db_engine, sequence_limit=10, verbose=False):
        self.db_engine = db_engine
        self.action = action
        self.root_action = action
        self.sequence_limit = sequence_limit
        self.verbose = verbose
        ## Initialize the AI client
        self.ai_client = None
        self.setup_client()

    def setup_client(self):
        """
        Setup the AI client with the necessary parameters.
        """
        load_dotenv()
        self.ai_client = anthropic.Anthropic()

    def start_action_id(self):
        """
        Get the action ID.
        """
        if self.action.action_id is None:
            # put or pull from the database
            table = AILoggingTables.AI_ACTION_LOG_TABLE
            data_row = {"action_name": self.action.name,
                "action_version": self.action.action_version,
                "parent_action_id": self.action.parent_action.action_id if self.action.parent_action else None,
                "group_action_id": self.action.group_action_id,
                "description": self.action.description,
                "sequence_number": self.action.sequence,
                "created_dt": datetime.datetime.now(),
                "updated_dt": datetime.datetime.now(),
                "status": self.action.status,
                "metadata": self.action.parameters,
            }
            action_id = self.db_engine.insert(table=table, data=data_row, output_data=['action_id'])[0][0]
            self.action.set_action_id(action_id=action_id)
            # db_engine.update(table=table, data={"updated_dt": datetime.datetime.now()}, where={"action_id": self.action_id})
        return action_id

    def run(self, user_prompt):
        """
        Run the action engine with the provided prompt.
        """
        step_cnt = 0
        while step_cnt < self.sequence_limit or self.action is None:
            self.start_action_id()
            # TODO: add a pre-engineer prompt step to extract parameters and validate.

            # Engineer the prompt based of the actions function
            prompt = self.action.engineer_prompt(user_prompt)

            # TODO: add a post-engineer prompt step to extract parameters
            # TODO: add an option to generate a think step-by-step option.

            # call the API
            # 1. The AI API will be called with the prompt, action settings
            # 2. Then use the validate_output method in the action class.
            # 3. If the output is valid, then log the action to the database.
            result = self.generate_action()

            # Complete Action
            self.action.complete_action()
            
            # Log the results to the database
            ls_next_steps = self.action.next_steps()
            step_cnt += 1
            self.action = ls_next_steps[0] if len(ls_next_steps) > 0 else None
        
    def generate_action(self, retry_cnt=2, **kwargs):
        current_retry = 0
        # Set default values for parameters
        kwargs = dict(**kwargs, **self.action.model_parameters)
        kwargs.setdefault("model", "claude-3-sonnet-latest")
        kwargs.setdefault("max_tokens", 2000)
        kwargs.setdefault("temperature", 0.1)
        kwargs.setdefault("stop_sequences", ["}"])
        kwargs["messages"] = self.action.get_messages()
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
            text_response = self.action.hygiene_output(text_response)
            # Set logging parameters
            duration = (response_timestamp - request_timestamp)
            duration_ms = (duration.total_seconds() * 1000) + duration.microseconds

            # Check if the response is valid JSON
            log_error = None
            try:
                if self.action.validate_output(text_response):
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
                    "action_id": self.action.action_id,
                    "insert_dt": datetime.datetime.now(),
                    "status": "SUCCESS" if log_error is None else "FAILED",
                    "ai_service": "Anthropic",
                    "model": kwargs["model"],
                    "request_parameters": {key: kwargs[key] for key in model_keys if key in kwargs},
                    "user_prompt": self.action.user_prompt,
                    "engineered_prompt": self.action.engineered_prompt,
                    "api_request_id": message._request_id,
                    "raw_response": message.content[0].text,
                    "parsed_results": text_response,
                    "response_metadate": {"role": message.role, 
                                        "stop_sequence": message.stop_sequence, 
                                        "stop_reason": message.stop_reason, 
                                        "usage": vars(message.usage)},
                    "input_tokens": message.usage.input_tokens,
                    "output_tokens": message.usage.output_tokens,
                    "request_timestamp": request_timestamp,
                    "response_timestamp": response_timestamp,
                    "duration_ms": duration_ms,
                    "error_code": log_error.code if log_error and hasattr(log_error.code) else None,
                    "error_message": None,
                    "error_timestamp": None,
                    "retry_cnt": retry_cnt,
                    "RAG_Embeding_Model": None,
                    "RAG_IDs": None,
                    "RAG_Versions": None,
                    "metadata": None,
                }
                self.db_engine.insert(table_name, data_row=data_row)
            #end while loop
        return message