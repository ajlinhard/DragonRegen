
from kafka import KafkaProducer, KafkaConsumer
import json
from .Task import Task
from ...MetaFort.AILoggingTopics import AILoggingTopics
from ...MetaFort.SysLogs.KafkaEngine import KafkaEngine
from .DataStructCreate import DataStructCreate

class KafkaAgent:
    def __init__(self, task_queue_topic: str=AILoggingTopics.AI_TASK_TOPIC, db_engine=None, group_id: str='default'):
        self.task_queue_topic = task_queue_topic
        self.group_id = group_id
        self.db_engine = db_engine if db_engine else self.default_engine()
        self.producer = KafkaProducer(bootstrap_servers=self.broker)
        self.consumer = KafkaConsumer(self.task_queue_topic, 
                                      bootstrap_servers=self.broker,
                                      group_id=self.group_id,
                                      auto_offset_reset='latest',)
        
    def default_engine(self):
        kafka_engine = KafkaEngine(
            connection_string='localhost:9092',
            )

        kafka_engine.producer = KafkaProducer(bootstrap_servers=['localhost:9092'], max_block_ms=5000)

        # Create Consumers
        kafka_engine.consumers[AILoggingTopics.AI_TASK_TOPIC] = KafkaConsumer(
                AILoggingTopics.AI_TASK_TOPIC,
                bootstrap_servers=['localhost:9092'],
                group_id='ai_logging_group',
                auto_offset_reset='latest')
        kafka_engine.consumers[AILoggingTopics.AI_TASK_LOG_TOPIC] = KafkaConsumer(
                AILoggingTopics.AI_TASK_LOG_TOPIC,
                bootstrap_servers=['localhost:9092'],
                group_id='ai_logging_group',
                auto_offset_reset='latest')
        
        return kafka_engine

    def initial_prompt(self, message: str):
        # TODO - Add code to decide the best initial agent.
        DataStructCreate()
        self.producer.send(self.task_queue_topic, value=json.dumps(message).encode('utf-8'))
        self.producer.flush()

    def receive_messages(self):
        task_queue = self.consumer.poll(timeout_ms=1000, max_records=10)
        for topic_partition, messages in task_queue.items():
            for message in messages:
                task_json = message.value.decode('utf-8')
                # For example, you can create an task object and execute it
                task = Task.get_task_type(task_json['task_name'])(task_json['input_params'])
