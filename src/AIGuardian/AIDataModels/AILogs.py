from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

class TaskArtifact(BaseModel):
    artifactId: str = Field(default=str(uuid.uuid4()), description="Primary key, unique identifier for an artifact produced by a task")
    task_id: str = Field(..., description="Foreign key, representing a specific task")
    group_task_id: Optional[str] = None
    insert_dt: datetime = Field(default=datetime.now(), description="Timestamp when the task was completed")
    name: str = Field(..., description="Name of the task")
    description: Optional[str] = None
    parts: List[Any] = Field(..., description="Content of the artifact, as one or more Part objects. Must have at least one.")
    metadata: Optional[Dict[str, Any]] = None
    extensions: Optional[Dict[str, Any]] = None


class TaskLog(BaseModel):
    task_id: str = Field(..., description="Primary key, unique identifier for the task")
    task_name: str = Field(..., description="Name of the task")
    task_version: str = Field(..., description="Then version of the task")
    parent_task_id: Optional[str] = None
    group_task_id: Optional[str] = None
    description: Optional[str] = None
    sequence_number: int = Field(..., description="Order of execution within the parent task")
    created_dt: datetime = Field(..., description="Timestamp when the task was created")
    updated_dt: datetime = Field(..., description="Timestamp when the task was last updated")
    input_artifacts: Optional[Dict[str, Any]] = None
    

class TaskCompleted(BaseModel):
    task_id: str = Field(..., description="Foreign key, but still a unique identifier for the task")
    task_name: str = Field(..., description="Name of the task")
    group_task_id: Optional[str] = None
    insert_dt: datetime = Field(..., description="Timestamp when the task was completed")
    output_artifacts: Optional[Dict[str, Any]] = None

class LLMRequest(BaseModel):
    request_id: str = Field(default=str(uuid.uuid4()), description="Primary key, unique identifier for the request")
    task_id: str = Field(..., description="Foreign key referencing the task log")
    insert_dt: datetime = Field(..., description="When the request was logged.")
    status: Optional[str] = None
    ai_service: str = Field(..., description="Name or identifier of the AI service being called")
    model: str = Field(..., description="Version of the AI model used (if applicable)")
    request_parameters: Optional[Dict[str, Any]] = None
    user_prompt: Optional[str] = None
    engineered_prompt: Optional[str] = None
    api_request_id: Optional[str] = None
    raw_response: str = Field(..., description="Raw response from the AI service")
    parsed_results: str = Field(..., description="Parsed results by the Task using the AI service response")
    response_metadate: Optional[Dict[str, Any]] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    request_timestamp: Optional[datetime] = None
    response_timestamp: Optional[datetime] = None
    duration_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_timestamp: Optional[datetime] = None
    retry_cnt: Optional[int] = None
    RAG_Embeding_Model: Optional[Dict[str, Any]] = None
    RAG_IDs: Optional[Dict[str, Any]] = None
    RAG_Versions: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None