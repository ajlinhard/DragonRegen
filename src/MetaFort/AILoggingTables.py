
class AILoggingTables():
    d_system_tables = {"actions": {
    "purpose": "Highest level object representing a group of related operations or tasks",
    "columns": [
      {"name": "action_id", "type": "Integer", "nullable": False, "metadata": "Primary key, unique identifier for the action"},
      {"name": "name", "type": "String", "nullable": False, "metadata": "Name of the action"},
      {"name": "description", "type": "String", "nullable": True, "metadata": "Detailed description of the action's purpose"},
      {"name": "created_at", "type": "Timestamp", "nullable": False, "metadata": "Timestamp when the action was created"},
      {"name": "updated_at", "type": "Timestamp", "nullable": False, "metadata": "Timestamp when the action was last updated"},
      {"name": "status", "type": "String", "nullable": False, "metadata": "Current status of the action (active, completed, failed, etc.)"},
      {"name": "error_code", "type": "String", "nullable": True, "metadata": "Error code if action failed"},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": "Detailed error message if action failed"},
      {"name": "error_timestamp", "type": "Timestamp", "nullable": True, "metadata": "When the error occurred at action level"},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": "JSON field for any additional action metadata"}
    ]
  },
  "sub_actions": {
    "purpose": "Middle level object representing specific operations within an action",
    "columns": [
      {"name": "sub_action_id", "type": "Integer", "nullable": False, "metadata": "Primary key, unique identifier for the sub-action"},
      {"name": "action_id", "type": "Integer", "nullable": False, "metadata": "Foreign key referencing the parent action"},
      {"name": "name", "type": "String", "nullable": False, "metadata": "Name of the sub-action"},
      {"name": "description", "type": "String", "nullable": True, "metadata": "Detailed description of the sub-action's purpose"},
      {"name": "sequence_number", "type": "Integer", "nullable": False, "metadata": "Order of execution within the parent action"},
      {"name": "created_at", "type": "Timestamp", "nullable": False, "metadata": "Timestamp when the sub-action was created"},
      {"name": "updated_at", "type": "Timestamp", "nullable": False, "metadata": "Timestamp when the sub-action was last updated"},
      {"name": "status", "type": "String", "nullable": False, "metadata": "Current status of the sub-action"},
      {"name": "error_code", "type": "String", "nullable": True, "metadata": "Error code if sub-action failed"},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": "Detailed error message if sub-action failed"},
      {"name": "error_timestamp", "type": "Timestamp", "nullable": True, "metadata": "When the error occurred at sub-action level"},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": "JSON field for any additional sub-action metadata"}
    ]
  },
  "requests": {
    "purpose": "Lowest level object representing individual API calls to AI services",
    "columns": [
      {"name": "request_id", "type": "Integer", "nullable": False, "metadata": "Primary key, unique identifier for the request"},
      {"name": "sub_action_id", "type": "Integer", "nullable": False, "metadata": "Foreign key referencing the parent sub-action"},
      {"name": "ai_service", "type": "String", "nullable": False, "metadata": "Name or identifier of the AI service being called"},
      {"name": "endpoint", "type": "String", "nullable": False, "metadata": "Specific API endpoint that was called"},
      {"name": "request_timestamp", "type": "Timestamp", "nullable": False, "metadata": "When the request was sent"},
      {"name": "response_timestamp", "type": "Timestamp", "nullable": True, "metadata": "When the response was received"},
      {"name": "duration_ms", "type": "Integer", "nullable": True, "metadata": "Processing time in milliseconds"},
      {"name": "status_code", "type": "Integer", "nullable": True, "metadata": "HTTP status code of the response"},
      {"name": "request_parameters", "type": "JSON", "nullable": False, "metadata": "JSON field containing all request parameters sent to the API"},
      {"name": "raw_response", "type": "JSON", "nullable": True, "metadata": "Full raw response from the API"},
      {"name": "parsed_results", "type": "JSON", "nullable": True, "metadata": "JSON field containing parsed/processed results"},
      {"name": "model_version", "type": "String", "nullable": True, "metadata": "Version of the AI model used (if applicable)"},
      {"name": "completion_tokens", "type": "Integer", "nullable": True, "metadata": "Number of tokens in the completion (for LLM APIs)"},
      {"name": "prompt_tokens", "type": "Integer", "nullable": True, "metadata": "Number of tokens in the prompt (for LLM APIs)"},
      {"name": "total_tokens", "type": "Integer", "nullable": True, "metadata": "Total tokens used in the interaction"},
      {"name": "cost", "type": "Float", "nullable": True, "metadata": "Cost of the API call (if applicable)"},
      {"name": "error_code", "type": "String", "nullable": True, "metadata": "Error code if request failed"},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": "Detailed error message if request failed"},
      {"name": "error_timestamp", "type": "Timestamp", "nullable": True, "metadata": "When the error occurred at request level"},
      {"name": "is_error_resolved", "type": "Boolean", "nullable": True, "metadata": "Indicates if the error has been resolved"},
      {"name": "resolution_notes", "type": "String", "nullable": True, "metadata": "Notes on how the error was resolved"},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": "JSON field for any additional request/response metadata"}
    ]
  },
  "metrics": {
    "purpose": "Stores aggregated performance metrics for analysis across all levels",
    "columns": [
      {"name": "metric_id", "type": "Integer", "nullable": False, "metadata": "Primary key, unique identifier for the metric record"},
      {"name": "action_id", "type": "Integer", "nullable": True, "metadata": "Foreign key referencing the associated action (if applicable)"},
      {"name": "sub_action_id", "type": "Integer", "nullable": True, "metadata": "Foreign key referencing the associated sub-action (if applicable)"},
      {"name": "request_id", "type": "Integer", "nullable": True, "metadata": "Foreign key referencing the associated request (if applicable)"},
      {"name": "metric_type", "type": "String", "nullable": False, "metadata": "Type of metric being recorded (performance, usage, etc.)"},
      {"name": "metric_name", "type": "String", "nullable": False, "metadata": "Name of the specific metric"},
      {"name": "value", "type": "Float", "nullable": False, "metadata": "Numeric value of the metric"},
      {"name": "unit", "type": "String", "nullable": True, "metadata": "Unit of measurement for the metric"},
      {"name": "timestamp", "type": "Timestamp", "nullable": False, "metadata": "When the metric was recorded"},
      {"name": "dimensions", "type": "JSON", "nullable": True, "metadata": "JSON field containing metric dimensions for analysis"}
    ]
  }
}