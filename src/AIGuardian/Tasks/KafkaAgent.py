
from kafka import KafkaProducer, KafkaConsumer
import json

# Internal Package Imports
from src.AIGuardian.Tasks.Task import Task
from src.MetaFort.AILoggingTopics import AILoggingTopics
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine
from src.AIGuardian.Tasks.DataStructCreate import DataStructCreate
from src.AIGuardian.Tasks.TaskRegistry import TaskRegistry

class KafkaAgent:
    def __init__(self, task_queue_topic: str=AILoggingTopics.AI_TASK_TOPIC, db_engine=None, group_id: str='default', end_processing: int=300):
        raise NotImplementedError("KafkaAgent is not implemented yet.") # look at DummyAgent.ipynb in docs
        self.task_queue_topic = task_queue_topic
        self.group_id = group_id
        self.root_action = None
        self.end_processing = end_processing
        self.db_engine = db_engine if db_engine else KafkaEngine.default_builder()

    def initial_prompt(self, message: str):
        # TODO - Add code to decide the best initial agent.
        self.root_action = DataStructCreate()
        self.root_action.db_engine = self.db_engine
        self.root_action.initialize()

    def receive_messages(self):
        task_queue = self.db_engine.consumers[AILoggingTopics.AI_TASK_TOPIC].poll(timeout_ms=1000, max_records=20)
        print(f"Task Queue: {task_queue}")
        task_list = []
        for topic_partition, messages in task_queue.items():
            for message in messages:
                if not isinstance(message.value, dict):
                    task_json = json.loads(message.value.decode('utf-8'))
                else:
                    task_json = message.value
                # For example, you can create an task object and execute it
                task = TaskRegistry.build_from_json(task_json, db_engine)
                print(f"Task Type: {type(task)}")
                # print(f"Task: {task.name} ==> {task.task_id} FROM ID {task_json['task_id']}")
                task_list.append(task)
        
        # Run the task polled by the Kafka consumer
        for task_item in task_list:
            print(f"Task: {task_item.name} ==> {task_item.task_id}")
            await task_item.run("")