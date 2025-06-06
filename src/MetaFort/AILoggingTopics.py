
class AILoggingTopics():
  AI_TASK_TOPIC = "ai_tasks"
  AI_TASK_ARTIFACTS_TOPIC = "ai_tasks_artifacts"
  AI_TASK_COMPLETED_TOPIC = "ai_tasks_completed"
  AI_TASK_LOG_TOPIC = "ai_tasks_log"
  AI_REQUEST_LOG_TOPIC = "ai_requests_log"
  AI_METRICS_LOG_TOPIC = "ai_metrics_log"
  d_system_topics = {
      AI_TASK_TOPIC: {
    "purpose": "Highest level table representing a tasks ready to be picked up by system to complete.",
    "fields": [
      {"name": "task_id", "type": "String", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the task"}},
      {"name": "task_name", "type": "String", "nullable": False, "metadata": {"description": "Name of the task"}},
      {"name": "task_version", "type": "String", "nullable": False, "metadata": {"description": "Then version of the task"}},
      {"name": "parent_task_id", "type": "String", "nullable": True, "metadata": {"description": "self referencing key of the parent task"}},
      {"name": "group_task_id", "type": "String", "nullable": True, "metadata": {"description": "Name of the a set of tasks that chained off each other. The value is the root task ID"}},
      {"name": "description", "type": "String", "nullable": True, "metadata": {"description": "Detailed description of the task's purpose"}},
      {"name": "sequence_number", "type": "Integer", "nullable": False, "metadata": {"description": "Order of execution within the parent task"}},
      {"name": "created_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "Timestamp when the task was created"}},
      {"name": "updated_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "Timestamp when the task was last updated"}},
      {"name": "input_artifacts", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field for any additional task metadata"}}
    ]
  },
  AI_TASK_ARTIFACTS_TOPIC: {
    "purpose": "The place for all artifacts to be published.",
    "fields": [
      {"name": "artifactId", "type": "String", "nullable": False, "metadata": {"description": "Primary key, unique identifier for an artifact produced by a task"}},
      {"name": "task_id", "type": "String", "nullable": False, "metadata": {"description": "Forgeign key, representing a specific task"}},
      {"name": "group_task_id", "type": "String", "nullable": True, "metadata": {"description": "Name of the a set of tasks that chained off each other. The value is the root task ID"}},
      {"name": "insert_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "Timestamp when the task was completed"}},
      # Google A2A Columns
      {"name": "name", "type": "String", "nullable": False, "metadata": {"description": "Name of the task"}},
      {"name": "description", "type": "JSON", "nullable": True, "metadata": {"description": "Human-readable description of the artifact."}},
      {"name": "parts", "type": "Array", "nullable": False, "metadata": {"description": "Content of the artifact, as one or more Part objects. Must have at least one."}},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": {"description": "Arbitrary key-value metadata associated with the artifact."}},
      {"name": "extensions", "type": "JSON", "nullable": True, "metadata": {"description": "A list of extension URIs that contributed to this artifact."}},
    ]
  },
  AI_TASK_COMPLETED_TOPIC: {
    "purpose": "Highest level table representing a tasks that completed",
    "fields": [
      {"name": "task_id", "type": "String", "nullable": False, "metadata": {"description": "Foreign key, but still a unique identifier for the task"}},
      {"name": "task_name", "type": "String", "nullable": False, "metadata": {"description": "Name of the task"}},
      {"name": "group_task_id", "type": "String", "nullable": True, "metadata": {"description": "Name of the a set of tasks that chained off each other. The value is the root task ID"}},
      {"name": "insert_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "Timestamp when the task was completed"}},
      {"name": "output_artifacts", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field for any additional task metadata"}}
    ]
  },
  AI_TASK_LOG_TOPIC: {
    "purpose": "Highest level object representing a group of related task or tasks",
    "fields": [
      {"name": "task_log_id", "type": "String", "nullable": False, "metadata": {"description": "Primary key, unique identifier for this log"}},
      {"name": "task_id", "type": "String", "nullable": False, "metadata": {"description": "Foreign key, unique identifier for the task"}},
      {"name": "task_name", "type": "String", "nullable": False, "metadata": {"description": "Name of the task"}},
      {"name": "group_task_id", "type": "Integer", "nullable": True, "metadata": {"description": "Name of the a set of tasks that chained off each other. The value is the root task ID"}},
      {"name": "log_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "Timestamp when the task was last updated"}},
      {"name": "task_state", "type": "String", "nullable": False, "metadata": {"description": "Current status of the task"}},
      {"name": "error_code", "type": "String", "nullable": True, "metadata": {"description": "Error code if task failed"}},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": {"description": "Detailed error message if task failed"}},
      {"name": "error_timestamp", "type": "Timestamp", "nullable": True, "metadata": {"description": "When the error occurred at task level"}},
      {"name": "metadata", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field for any additional task metadata"}}
    ]
  },
  AI_REQUEST_LOG_TOPIC: {
    "purpose": "Lowest level object representing individual API calls to AI services",
    "fields": [
      {"name": "request_id", "type": "String", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the request"}},
      {"name": "task_id", "type": "String", "nullable": False, "metadata": {"description": "Foreign key referencing the task log"}},
      {"name": "insert_dt", "type": "Timestamp", "nullable": False, "metadata": {"description": "When the request was logged."}},
      {"name": "status", "type": "String", "nullable": True, "metadata": {"description": "Status of the request (SUCCESS, FAILURE, PENDING)"}},
      # Model specific fields
      {"name": "ai_service", "type": "String", "nullable": False, "metadata": {"description": "Name or identifier of the AI service being called"}},
      {"name": "model", "type": "String", "nullable": False, "metadata": {"description": "Version of the AI model used (if applicable)"}},
      {"name": "request_parameters", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field containing all request parameters sent to the API"}},
      {"name": "user_prompt", "type": "String", "nullable": True, "metadata": {"description": "The original user prompt sent to the application."}},
      {"name": "engineered_prompt", "type": "String", "nullable": True, "metadata": {"description": "The altered prompt sent to the AI service."}},
      # response fields
      {"name": "api_request_id", "type": "String", "nullable": True, "metadata": {"description": "Foreign key referencing the request id returned by the API. Usually a "}},
      {"name": "raw_response", "type": "JSON", "nullable": True, "metadata": {"description": "Full raw response from the API"}},
      {"name": "parsed_results", "type": "JSON", "nullable": True, "metadata": {"description": "JSON field containing parsed/processed results"}},
      {"name": "response_metadata", "type": "JSON", "nullable": True, "metadata": {"description": "Additional metadata from the API response"}},
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
  AI_METRICS_LOG_TOPIC: {
    "purpose": "Stores aggregated performance metrics for analysis across all levels",
    "fields": [
      {"name": "metric_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the metric record"}},
      {"name": "task_id", "type": "Integer", "nullable": True, "metadata": {"description": "Foreign key referencing the associated task (if applicable)"}},
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