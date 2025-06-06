import json
from src.AIGuardian.Tasks.TaskExceptions import ValidateAIResponseError

class GenAIUtils():
    
    VALID_OUTPUT_TYPES = ["Text", "JSON", "AITool", "ActionList", "Action"]

    @staticmethod
    def prompt_dict_substitute(prompt, **kwargs):
        """
        Substitute the prompt with the given parameters.
        """
        # Substitute the prompt with the given parameters
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))
        return prompt
    
    @staticmethod
    def hygiene_to_json(text_response):
        """
        Clean the output of the action.
        """
        # Check if the last and first characters are brackets
        text_response = text_response.replace("<JSON_Template>", "")
        text_response = text_response.replace("</JSON_Template>", "")
        text_response = text_response.strip()
        if text_response[0] != '{':
            # Remove the first and last characters
            text_response = '{' + text_response
        if text_response[-1] != '}':
            text_response += '}'
        return text_response
    
    @staticmethod
    def validate_json(text_response):
        """
        Validate the JSON response.
        """
        # Check if the response is valid JSON
        try:
            json.loads(text_response)
            return True
        except json.JSONDecodeError as e:
            # Get error position
            pos = e.pos
            # Calculate start and end positions for context
            start = max(0, pos - 10)
            end = min(len(text_response), pos + 10)
            # Extract the context around the error
            context = text_response[start:end]
            new_error_msg = f"Error message: {str(e)}" + \
                f"Error position: line {e.lineno}, column {e.colno}" + \
                f"Error Line Context: {context}" + \
                f"Error document: {e.doc}"
            raise ValidateAIResponseError(new_error_msg)
        return False
    
    @staticmethod
    def validate_json_w_key_check(json_response, key_struct):
        """
        Validate the JSON response.
        """
        # Check if the response is valid JSON
        if GenAIUtils.validate_json(json_response):
            # Check if the JSON response contains the required keys
            for key in key_struct:
                if key not in json_response:
                    raise ValidateAIResponseError(f"Missing key: {key} in JSON response")
            return True
        return False
    
    @staticmethod
    def valid_output_type(output_type):
        """
        Validate the output type of the action.
        """
        # Check if the output type is a valid string
        if output_type not in VALID_OUTPUT_TYPES:
            raise ValueError(f"Invalid output type: {output_type}. Must be in {__class__.__name__}.VALID_OUTPUT_TYPES")
        return output_type


    @staticmethod
    def generate_json(ai_client, retry_cnt=2, **kwargs):
        """
        Generate a JSON object using the AI client.
        """
        current_retry = 0
        # Set default values for parameters
        kwargs.setdefault("model", "claude-3-sonnet-latest")
        kwargs.setdefault("max_tokens", 2000)
        kwargs.setdefault("temperature", 0.1)
        kwargs.setdefault("stop_sequences", ["}"])
        
        message = None
        # Generate the JSON object using the AI client
        while(current_retry < retry_cnt):
            current_retry += 1
            # Send the request to the AI client
            message = ai_client.messages.create(**kwargs)
            json_response = message.content[0].text
            # Check if the response is valid JSON
            try:
                json.loads(json_response)
                break  # Exit the loop if JSON is valid
            except json.JSONDecodeError as e:
                 # Get error position
                pos = e.pos
                # Calculate start and end positions for context
                start = max(0, pos - 10)
                end = min(len(json_response), pos + 10)
                # Extract the context around the error
                context = json_response[start:end]
                print(f"Error message: {str(e)}")
                print(f"Error position: line {e.lineno}, column {e.colno}")
                print(f"Error Line Context: {context}")
                print(f"Error document: {e.doc}")
            else:
                raise ValueError(f"Invalid JSON response: {json_response} after {current_retry} retries")
        return message
