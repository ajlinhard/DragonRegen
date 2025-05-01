
class AILoggingTables():
    d_system_tables = {
  "actions": {
    "purpose": "Highest level object representing a group of related action or tasks",
    "fields": [
      {"name": "action_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the action"}},
      {"name": "action_name", "type": "String", "nullable": False, "metadata": {"description": "Name of the action"}},
      {"name": "action_version", "type": "String", "nullable": False, "metadata": {"description": "Then version of the action"}},
      {"name": "action_description", "type": "String", "nullable": False, "metadata": {"description": "description of the action"}},
      {"name": "parent_action_id", "type": "Integer", "nullable": False, "metadata": {"description": "self referencing key of the parent action"}},
      {"name": "group_action_id", "type": "Integer", "nullable": False, "metadata": {"description": "Name of the a set of actions that chained off each other. The value is the root action ID"}},
      {"name": "description", "type": "String", "nullable": True, "metadata": {"description": "Detailed description of the action's purpose"}},
      {"name": "sequence_number", "type": "Integer", "nullable": False, "metadata": {"description": "Order of execution within the parent action"}},
      {"name": "created_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "Timestamp when the sub-action was created"}},
      {"name": "updated_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "Timestamp when the sub-action was last updated"}},
      {"name": "status", "type": "String", "nullable": False, "metadata": {"description": "Current status of the sub-action"}},
      {"name": "error_code", "type": "String", "nullable": True, "metadata": {"description": "Error code if sub-action failed"}},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": {"description": "Detailed error message if sub-action failed"}},
      {"name": "error_timestamp", "type": "Timestamp", "nullable": True, "metadata": {"description": "When the error occurred at sub-action level"}},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field for any additional sub-action metadata"}}
    ]
  },
  "requests": {
    "purpose": "Lowest level object representing individual API calls to AI services",
    "fields": [
      {"name": "request_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the request"}},
      {"name": "action_id", "type": "Integer", "nullable": False, "metadata": {"description": "Foreign key referencing the parent action"}},
      {"name": "ai_service", "type": "String", "nullable": False, "metadata": {"description": "Name or identifier of the AI service being called"}},
      {"name": "endpoint", "type": "String", "nullable": False, "metadata": {"description": "Specific API endpoint that was called"}},
      {"name": "request_timestamp", "type": "Timestamp", "nullable": False, "metadata": {"description": "When the request was sent"}},
      {"name": "response_timestamp", "type": "Timestamp", "nullable": True, "metadata": {"description": "When the response was received"}},
      {"name": "duration_ms", "type": "Integer", "nullable": True, "metadata": {"description": "Processing time in milliseconds"}},
      {"name": "status_code", "type": "Integer", "nullable": True, "metadata": {"description": "HTTP status code of the response"}},
      {"name": "request_parameters", "type": "JSON", "nullable": False, "metadata": {"description": "JSON field containing all request parameters sent to the API"}},
      {"name": "raw_response", "type": "JSON", "nullable": True, "metadata": {"description": "Full raw response from the API"}},
      {"name": "parsed_results", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field containing parsed/processed results"}},
      {"name": "model_version", "type": "String", "nullable": True, "metadata": {"description": "Version of the AI model used (if applicable)"}},
      {"name": "completion_tokens", "type": "Integer", "nullable": True, "metadata": {"description": "Number of tokens in the completion (for LLM APIs)"}},
      {"name": "prompt_tokens", "type": "Integer", "nullable": True, "metadata": {"description": "Number of tokens in the prompt (for LLM APIs)"}},
      {"name": "total_tokens", "type": "Integer", "nullable": True, "metadata": {"description": "Total tokens used in the interaction"}},
      {"name": "cost", "type": "Float", "nullable": True, "metadata": {"description": "Cost of the API call (if applicable)"}},
      {"name": "error_code", "type": "String", "nullable": True, "metadata": {"description": "Error code if request failed"}},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": {"description": "Detailed error message if request failed"}},
      {"name": "error_timestamp", "type": "Timestamp", "nullable": True, "metadata": {"description": "When the error occurred at request level"}},
      {"name": "is_error_resolved", "type": "Boolean", "nullable": True, "metadata": {"description": "Indicates if the error has been resolved"}},
      {"name": "resolution_notes", "type": "String", "nullable": True, "metadata": {"description": "Notes on how the error was resolved"}},
      {"name": "RAG_IDs", "type": "JSON", "nullable": True, "metadata": {"description": "List of IDs for RAG (Retrieval-Augmented Generation) documents used in the request"}},
      {"name": "RAG_Versions", "type": "JSON", "nullable": True, "metadata": {"description": "List of versions for RAG documents used in the request"}},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field for any additional request/response metadata"}}
    ]
  },
  "metrics": {
    "purpose": "Stores aggregated performance metrics for analysis across all levels",
    "fields": [
      {"name": "metric_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the metric record"}},
      {"name": "action_id", "type": "Integer", "nullable": True, "metadata": {"description": "Foreign key referencing the associated action (if applicable)"}},
      {"name": "sub_action_id", "type": "Integer", "nullable": True, "metadata": {"description": "Foreign key referencing the associated sub-action (if applicable)"}},
      {"name": "request_id", "type": "Integer", "nullable": True, "metadata": {"description": "Foreign key referencing the associated request (if applicable)"}},
      {"name": "metric_type", "type": "String", "nullable": False, "metadata": {"description": "Type of metric being recorded (performance, usage, etc.)"}},
      {"name": "metric_name", "type": "String", "nullable": False, "metadata": {"description": "Name of the specific metric"}},
      {"name": "value", "type": "Float", "nullable": False, "metadata": {"description": "Numeric value of the metric"}},
      {"name": "unit", "type": "String", "nullable": True, "metadata": {"description": "Unit of measurement for the metric"}},
      {"name": "timestamp", "type": "Timestamp", "nullable": False, "metadata": {"description": "When the metric was recorded"}},
      {"name": "dimensions", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field containing metric dimensions for analysis"}}
    ]
  }
}