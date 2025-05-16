
from kafka import KafkaProducer, KafkaConsumer
import json
from .Task import Task
from ...MetaFort.AILoggingTopics import AILoggingTopics
from ...MetaFort.SysLogs.KafkaEngine import KafkaEngine
from .DataStructCreate import DataStructCreate

class KafkaAgent:
    def __init__(self, task_queue_topic: str=AILoggingTopics.AI_TASK_TOPIC, db_engine=None, group_id: str='default'):
        raise NotImplementedError("KafkaAgent is not implemented yet.") # look at DummyAgent.ipynb in docs
        self.task_queue_topic = task_queue_topic
        self.group_id = group_id
        self.root_action = None
        self.db_engine = db_engine if db_engine else KafkaEngine.default_builder()

    def initial_prompt(self, message: str):
        # TODO - Add code to decide the best initial agent.
        self.root_action = DataStructCreate()
        self.root_action.db_engine = self.db_engine
        self.root_action.initialize()

    def receive_messages(self):
        task_queue = self.consumer.poll(timeout_ms=1000, max_records=10)
        for topic_partition, messages in task_queue.items():
            for message in messages:
                task_json = message.value.decode('utf-8')
                # For example, you can create an task object and execute it
                task = Task.get_task_type(task_json['task_name'])(task_json['input_params'])
