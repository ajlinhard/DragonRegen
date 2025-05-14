
import datetime
import json
from kafka import KafkaProducer, KafkaConsumer
from typing import Dict, List, Optional, Any, Union
from ...MetaFort.AILoggingTopics import AILoggingTopics

class KafkaEngine():
    """Base class for database connection handling"""
    d_log_tables = {"dyn_sql_execution_log": {
    "purpose": "Track the execution of dynamic SQL commands",
    "fields": [
      {"name": "execution_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the execution"}},
      {"name": "sql_command", "type": "String", "nullable": False, "metadata": {"description": "The SQL command that was executed"}},
      {"name": "sql_params", "type": "String", "nullable": False, "metadata": {"description": "The list of parameters used to replace the placeholders in the SQL command"}},
      {"name": "start_time", "type": "String", "nullable": False, "metadata": {"description": "Timestamp when the command was executed"}},
      {"name": "stop_time", "type": "String", "nullable": False, "metadata": {"description": "Timestamp when the command was executed"}},
      {"name": "status", "type": "String", "nullable": False, "metadata": {"description": "Status of the execution (success, failure)"}},
      {"name": "user_name", "type": "String", "nullable": False, "metadata": {"description": "Error message if execution failed"}},
      {"name": "process_id", "type": "String", "nullable": False, "metadata": {"description": "Processing ID initiation time. This plus Process ID should be unique on the server/system."}},
      {"name": "process_login_time", "type": "Timestamp", "nullable": False, "metadata": {"description": "Processing ID of the execution"}},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": {"description": "Error message if execution failed"}},
      {"name": "error_timestamp", "type": "String", "nullable": True, "metadata": {"description": "When the error occurred"}},
      {"name": "metadata", "type": "JSON", "nullable": True,  # Assuming JSON is a valid type in your database
      	"metadata": {"description":"JSON field for any additional metadata related to the execution"}}
    ]
    }}
    
    def __init__(self, connection_string: str, autocommit: bool = True, verbose: bool = False):
        """Initialize database connection
        
        Args:
            connection_string: Connection string for the database
        """
        self.connection_string = connection_string
        self.autocommit = autocommit
        self.verbose = verbose
        # Kafka Specific
        self.producer = None
        self.consumers = {}
    
    @classmethod
    def default_builder(cls, group_id: str = 'default') -> 'KafkaEngine':
        """Create a default KafkaEngine instance
        Returns:
            KafkaEngine: Default KafkaEngine instance
        """
        # Initialize KafkaEngine
        kafka_engine = cls(
            connection_string='localhost:9092',
        )

        kafka_engine.producer = KafkaProducer(bootstrap_servers=['localhost:9092'], max_block_ms=5000)

        # Create Consumers
        kafka_engine.consumers[AILoggingTopics.AI_TASK_TOPIC] = KafkaConsumer(
                AILoggingTopics.AI_TASK_TOPIC,
                bootstrap_servers=['localhost:9092'],
                group_id=group_id,
                auto_offset_reset='latest')
        kafka_engine.consumers[AILoggingTopics.AI_TASK_LOG_TOPIC] = KafkaConsumer(
                AILoggingTopics.AI_TASK_LOG_TOPIC,
                bootstrap_servers=['localhost:9092'],
                group_id=group_id,
                auto_offset_reset='latest')
        kafka_engine.consumers[AILoggingTopics.AI_TASK_COMPLETED_TOPIC] = KafkaConsumer(
                AILoggingTopics.AI_TASK_COMPLETED_TOPIC,
                bootstrap_servers=['localhost:9092'],
                group_id=group_id,
                auto_offset_reset='latest')
        return kafka_engine

    def has_producer(self, topic: str) -> bool:
        """Check if a producer for the given topic exists
        
        Args:
            topic: Topic name
        
        Returns:
            bool: True if producer exists, False otherwise
        """
        return self.producer is not None
    
    def has_consumer(self, topic: str) -> bool:
        """Check if a consumer for the given topic exists
        
        Args:
            topic: Topic name
        
        Returns:
            bool: True if consumer exists, False otherwise
        """
        return topic in self.consumers.keys()
    
    def insert(self, topic: str, data: Union[str, Dict[str, Any]]) -> bool:
        """Insert data into the specified topic
        
        Args:
            topic: Topic name
            data: Data to insert (can be a string or a dictionary)
        
        Returns:
            bool: True if insertion was successful, False otherwise
        """
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        
        self.producer.send(topic, value=data)
        self.producer.flush()
        return True
    
    def verify_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Verify if the data row matches the schema
        
        Args:
            data: Data row to verify
            schema: Schema to verify against
        
        Returns:
            bool: True if data row matches schema, False otherwise
        """
        # TODO link up to the schema registry
        col_names = []
        col_types = {}
        for field in schema['fields']:
            col_names.append(field['name'])
            col_types[field['name']] = field['type']
        
        for field in data.keys():
            if field not in col_names:
                return False
            # TODO add data type checking
            # if not isinstance(data[field_name], field_type):
            #     return False
        return True