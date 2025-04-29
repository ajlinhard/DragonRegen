import json

class GenAIUtils():

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
                print(f"Error message: {str(e)}")
                print(f"Error position: line {e.lineno}, column {e.colno}")
                print(f"Error document: {e.doc}")
        return message
