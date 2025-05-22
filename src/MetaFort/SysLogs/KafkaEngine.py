
import json
from datetime import datetime, timedelta
import time
import uuid
from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaConsumer, TopicPartition
from kafka.errors import TopicAlreadyExistsError
from typing import Dict, List, Optional, Any, Union

# Internal Package Imports
from src.MetaFort.AILoggingTopics import AILoggingTopics

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
        self.producer = KafkaProducer(bootstrap_servers=[self.connection_string], max_block_ms=5000)
        self.consumers = {}
        self.topic_uuid = str(uuid.uuid4())
    
    @staticmethod
    def initialize_system(connection_string: str):
        """
        Initialize the system with the given connection string:
         - Create Kafka topics if they do not exist
         - set up enough partitions and replication factor
         - set up the schema registry (if is confluent kafka)
        This is a static method and does not require an instance of the class to be called.
        
        Args:
            connection_string: Connection string for the database
        
        Returns:
        """
        # Initialize the admin client
        admin_client = KafkaAdminClient(
            bootstrap_servers=['localhost:9092'],
            client_id='my-admin-client'
        )

        # Topic configuration
        topic_name = "my-test-topic"
        num_partitions = 3
        replication_factor = 1

        # Create a NewTopic object
        new_topics = [AILoggingTopics.AI_TASK_TOPIC,
                        AILoggingTopics.AI_REQUEST_LOG_TOPIC,
                        AILoggingTopics.AI_TASK_LOG_TOPIC,
                        AILoggingTopics.AI_TASK_COMPLETED_TOPIC,
                    ]  
        partition_cnt = [5, 5, 5, 5]
        replication_factor = [1, 1, 1, 1]
        
        # zip together the topics and their configurations, to create them
        for topic, partitions, replication in zip(new_topics, partition_cnt, replication_factor):
            new_topic = NewTopic(
                name=topic,
                num_partitions=partitions,
                replication_factor=replication
            )
            try:
                admin_client.create_topics([new_topic])
                print(f"Topic {topic} created successfully")
            except TopicAlreadyExistsError:
                continue

        admin_client.close()

    @classmethod
    def default_builder(cls, subset_objects:List[str] = [], group_id={}) -> 'KafkaEngine':
        """Create a default KafkaEngine instance
        Returns:
            KafkaEngine: Default KafkaEngine instance
        """
        # Initialize KafkaEngine
        kafka_engine = cls(
            connection_string='localhost:9092',
        )
        KafkaEngine.initialize_system(kafka_engine.connection_string)
        

        # Create Consumers
        if subset_objects == [] or AILoggingTopics.AI_TASK_TOPIC in subset_objects:
            kafka_engine.consumers[AILoggingTopics.AI_TASK_TOPIC] = KafkaConsumer(
                AILoggingTopics.AI_TASK_TOPIC,
                bootstrap_servers=['localhost:9092'],
                group_id=group_id.get(AILoggingTopics.AI_TASK_TOPIC, 'action-agent'),
                auto_offset_reset='latest')
        if subset_objects == [] or AILoggingTopics.AI_REQUEST_LOG_TOPIC in subset_objects:
            kafka_engine.consumers[AILoggingTopics.AI_REQUEST_LOG_TOPIC] = KafkaConsumer(
                    AILoggingTopics.AI_REQUEST_LOG_TOPIC,
                    bootstrap_servers=['localhost:9092'],
                    group_id=group_id.get(AILoggingTopics.AI_REQUEST_LOG_TOPIC, f'task-request-log-{kafka_engine.topic_uuid}'),
                    auto_offset_reset='latest')
        if subset_objects == [] or AILoggingTopics.AI_TASK_LOG_TOPIC in subset_objects:
            kafka_engine.consumers[AILoggingTopics.AI_TASK_LOG_TOPIC] = KafkaConsumer(
                    AILoggingTopics.AI_TASK_LOG_TOPIC,
                    bootstrap_servers=['localhost:9092'],
                    group_id=group_id.get(AILoggingTopics.AI_TASK_LOG_TOPIC, f'task-log-{kafka_engine.topic_uuid}'),
                    auto_offset_reset='latest')
        if subset_objects == [] or AILoggingTopics.AI_TASK_COMPLETED_TOPIC in subset_objects:
            kafka_engine.consumers[AILoggingTopics.AI_TASK_COMPLETED_TOPIC] = KafkaConsumer(
                    AILoggingTopics.AI_TASK_COMPLETED_TOPIC,
                    bootstrap_servers=['localhost:9092'],
                    group_id=group_id.get(AILoggingTopics.AI_TASK_COMPLETED_TOPIC, f'task-completed-{kafka_engine.topic_uuid}'),
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
    
    def insert(self, topic: str, data, key:str = None) -> bool:
        """Insert data into the specified topic
        
        Args:
            topic: Topic name
            data: Data to insert (can be a string or a dictionary)
        
        Returns:
            bool: True if insertion was successful, False otherwise
        """
        if isinstance(data, dict):
            data = json.dumps(data).encode('utf-8')
        
        self.producer.send(topic, key=key, value=data)
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
    
    def close(self):
        """Close the database connection"""
        if self.producer:
            self.producer.close()
        for consumer in self.consumers.values():
            consumer.close()

    ## region Kafka Specific Tools

    def search_batch_topic(self, topic_name, search_value, search_key:str=None, bootstrap_servers=['localhost:9092'], 
                        timeout_seconds=60, from_beginning=True, deserializer=None):
        """
        Search through a Kafka topic for messages containing a specific value.
        
        Parameters:
        - topic_name: Name of the Kafka topic to search
        - search_value: The value to search for (can be string, int, etc.)
        - bootstrap_servers: Kafka broker addresses
        - timeout_seconds: How long to search before giving up (in seconds)
        - from_beginning: Whether to search from the beginning of the topic or recent messages
        - deserializer: Optional function to deserialize message values (default: attempt JSON)
        
        Returns:
        - List of matching messages with metadata
        """
        # Set up the consumer (no group ID needed for searching because we won't commit offsets)
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=self.connection_string,
            auto_offset_reset='earliest' if from_beginning else 'latest',
            enable_auto_commit=False,  # Don't commit offsets since we're just searching
            consumer_timeout_ms=timeout_seconds * 1000  # Stop consuming after timeout
        )
        
        matching_messages = []
        start_time = datetime.now()
        
        print(f"Searching topic '{topic_name}' for value: {search_value}")
        print(f"This will timeout after {timeout_seconds} seconds if no more messages are available.")
        
        # Default deserializer tries JSON, falls back to string
        if deserializer is None:
            def default_deserializer(value):
                if value is None:
                    return None
                try:
                    return json.loads(value.decode('utf-8'))
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return value.decode('utf-8', errors='replace')
            deserializer = default_deserializer
        
        # Start consuming messages
        message_count = 0
        try:
            while True:
                messages = consumer.poll(timeout_ms=1000, max_records=5000)
                if not messages and message_count > 0:
                    break  # No more messages to consume
                    
                for partition, msgs in messages.items():
                    message_count += len(msgs)
                    print(f"Processing {len(msgs)} messages from partition {partition}")
                    for message in msgs:
                        # Print progress every 1000 messages
                        if message_count % 1000 == 0:
                            elapsed = (datetime.now() - start_time).total_seconds()
                            print(f"Processed {message_count} messages in {elapsed:.2f} seconds...")
                        
                        # Deserialize the message value
                        try:
                            value = deserializer(message.value)
                        except Exception as e:
                            print(f"Error deserializing message: {e}")
                            continue
                        
                        # Check if the search value exists in the message
                        found = False
                        if search_key:
                            # If a search key is provided, check if the key exists in the message
                            if isinstance(value, dict) and search_key in value:
                                found = value[search_key] == search_value
                        else:
                            # If no search key is provided, check the entire message
                            found = self.record_search(value, search_value)
                        
                        # If found, add to our results
                        if found:
                            matching_messages.append({
                                'topic': message.topic,
                                'partition': message.partition,
                                'offset': message.offset,
                                'timestamp': message.timestamp,
                                'key': message.key.decode('utf-8') if message.key else None,
                                'value': value
                            })
                            print(f"Found match at offset {message.offset} in partition {message.partition}")
                    
        except StopIteration:
            # Consumer timeout reached
            pass
        finally:
            consumer.close()
        
        # Print summary
        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"Search completed in {elapsed_time:.2f} seconds.")
        print(f"Processed {message_count} messages, found {len(matching_messages)} matches.")
        
        return matching_messages
    
    def record_search(self, value, search_value):
        """
        Check if the search_value is anywhere in the value.
        This is a recursive function that checks all levels of the value.
        The search is an expensive but thorough search of kafka messages.
        """
        # For string values, check for substring
        if isinstance(value, str) and isinstance(search_value, str):
            found = search_value in value
        # For dictionaries (JSON objects), check all values recursively
        elif isinstance(value, dict):
            def check_dict(d, search_val):
                for k, v in d.items():
                    if isinstance(v, dict):
                        if check_dict(v, search_val):
                            return True
                    elif isinstance(v, list):
                        if check_list(v, search_val):
                            return True
                    elif str(search_val) == str(v):
                        return True
                return False
            
            def check_list(lst, search_val):
                for item in lst:
                    if isinstance(item, dict):
                        if check_dict(item, search_val):
                            return True
                    elif isinstance(item, list):
                        if check_list(item, search_val):
                            return True
                    elif str(search_val) == str(item):
                        return True
                return False
            
            found = check_dict(value, search_value)
        # For other types, convert to string and compare
        else:
            found = str(search_value) == str(value)


    def listify(self, kafka_records, key):
        """
        Convert a value to a list if it is not already a list.
        """
        kafka_list = []
        for topic_partition, messages in kafka_records.items():
            for message in messages:
                if not isinstance(message.value, dict):
                    task_json = json.loads(message.value.decode('utf-8'))
                else:
                    task_json = message.value
                val = task_json.get(key)
                kafka_list.append(val)
        return kafka_list
    

    def search_kafka_by_time(self, topic, search_value, start_time, end_time, bootstrap_servers=['localhost:9092']):
        """Search Kafka messages within a specific time range"""
        
        # Convert times to milliseconds since epoch
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)
        
        # Get partitions for the topic
        partitions = consumer.partitions_for_topic(topic)
        if not partitions:
            print(f"Topic {topic} not found")
            return []
        
        # Create TopicPartition objects
        topic_partitions = [TopicPartition(topic, p) for p in partitions]
        consumer.assign(topic_partitions)
        
        # Find offsets for the time range for each partition
        timestamps = {tp: start_ms for tp in topic_partitions}
        offsets = consumer.offsets_for_times(timestamps)
        
        # Assign starting positions
        for tp, offset_and_timestamp in offsets.items():
            if offset_and_timestamp:  # Can be None if no messages after start_time
                consumer.seek(tp, offset_and_timestamp.offset)
            else:
                # No messages after start_time in this partition
                consumer.seek_to_end(tp)
        
        # Search for messages within the time range
        matches = []
        for message in consumer:
            # Stop if we're past the end time
            if message.timestamp > end_ms:
                break
                
            # Check if value matches
            try:
                value = json.loads(message.value.decode('utf-8'))
            except:
                value = message.value.decode('utf-8', errors='replace')
                
            # Your matching logic here (can reuse from previous example)
            if str(search_value) in str(value):
                matches.append({
                    'topic': message.topic,
                    'partition': message.partition,
                    'offset': message.offset,
                    'timestamp': message.timestamp,
                    'value': value
                })
        
        consumer.close()
        return matches
