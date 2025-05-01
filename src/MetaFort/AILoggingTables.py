
class AILoggingTables():
  AI_ACTION_LOG_TABLE = "ai_actions_log"
  AI_REQUEST_LOG_TABLE = "ai_requests_log"
  AI_METRICS_LOG_TABLE = "ai_metrics_log"
  d_system_tables = {
  AI_ACTION_LOG_TABLE: {
    "purpose": "Highest level object representing a group of related action or tasks",
    "fields": [
      {"name": "action_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the action"}},
      {"name": "action_name", "type": "String", "nullable": False, "metadata": {"description": "Name of the action"}},
      {"name": "action_version", "type": "String", "nullable": False, "metadata": {"description": "Then version of the action"}},
      {"name": "parent_action_id", "type": "Integer", "nullable": True, "metadata": {"description": "self referencing key of the parent action"}},
      {"name": "group_action_id", "type": "Integer", "nullable": True, "metadata": {"description": "Name of the a set of actions that chained off each other. The value is the root action ID"}},
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
  AI_REQUEST_LOG_TABLE: {
    "purpose": "Lowest level object representing individual API calls to AI services",
    "fields": [
      {"name": "request_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the request"}},
      {"name": "action_id", "type": "Integer", "nullable": False, "metadata": {"description": "Foreign key referencing the action log"}},
      {"name": "insert_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "When the request was logged."}},
      {"name": "status", "type": "String", "nullable": True, "metadata": {"description": "Status of the request (SUCCESS, FAILURE, PENDING)"}},
      # Model specific fields
      {"name": "ai_service", "type": "String", "nullable": False, "metadata": {"description": "Name or identifier of the AI service being called"}},
      {"name": "model", "type": "String", "nullable": True, "metadata": {"description": "Version of the AI model used (if applicable)"}},
      {"name": "request_parameters", "type": "JSON", "nullable": False, "metadata": {"description": "JSON field containing all request parameters sent to the API"}},
      {"name": "user_prompt", "type": "String", "nullable": True, "metadata": {"description": "The original user prompt sent to the application."}},
      {"name": "engineered_prompt", "type": "String", "nullable": True, "metadata": {"description": "The altered prompt sent to the AI service."}},
      # response fields
      {"name": "api_request_id", "type": "Integer", "nullable": True, "metadata": {"description": "Foreign key referencing the request id returned by the API"}},
      {"name": "raw_response", "type": "JSON", "nullable": True, "metadata": {"description": "Full raw response from the API"}},
      {"name": "parsed_results", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field containing parsed/processed results"}},
      {"name": "response_metadate", "type": "JSON", "nullable": True, "metadata": {"description": "Additional metadata from the API response"}},
      {"name": "input_tokens", "type": "Integer", "nullable": True, "metadata": {"description": "Number of tokens in the prompt (for LLM APIs)"}},
      {"name": "output_tokens", "type": "Integer", "nullable": True, "metadata": {"description": "Total tokens used to create the response (for LLM APIs)"}},
      {"name": "request_timestamp", "type": "Timestamp", "nullable": True, "metadata": {"description": "When the request was sent"}},
      {"name": "response_timestamp", "type": "Timestamp", "nullable": True, "metadata": {"description": "When the response was received"}},
      {"name": "duration_ms", "type": "Integer", "nullable": True, "metadata": {"description": "Processing time in milliseconds"}},
      # error checking
      {"name": "error_code", "type": "String", "nullable": True, "metadata": {"description": "Error code if request failed"}},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": {"description": "Detailed error message if request failed"}},
      {"name": "error_timestamp", "type": "Timestamp", "nullable": True, "metadata": {"description": "When the error occurred at request level"}},
      {"name": "retry_cnt", "type": "Integer", "nullable": True, "metadata": {"description": "Indicates number of times a validation or re-attempt error has been flagged."}},
      # RAG specific fields
      {"name": "RAG_Embeding_Model", "type": "JSON", "nullable": True, "metadata": {"description": "List of models used for RAG (Retrieval-Augmented Generation) documents"}},
      {"name": "RAG_IDs", "type": "JSON", "nullable": True, "metadata": {"description": "List of IDs for RAG (Retrieval-Augmented Generation) documents used in the request"}},
      {"name": "RAG_Versions", "type": "JSON", "nullable": True, "metadata": {"description": "List of versions for RAG documents used in the request"}},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field for any additional request/response metadata"}}
    ]
  },
  AI_METRICS_LOG_TABLE: {
    "purpose": "Stores aggregated performance metrics for analysis across all levels",
    "fields": [
      {"name": "metric_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the metric record"}},
      {"name": "action_id", "type": "Integer", "nullable": True, "metadata": {"description": "Foreign key referencing the associated action (if applicable)"}},
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