
from kafka import KafkaProducer, KafkaConsumer
import json
from datetime import datetime
from typing import List, Dict, Any
import logging

# Internal Package Imports
from src.AIGuardian.Tasks.Task import Task
from src.MetaFort.AILoggingTopics import AILoggingTopics
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine
from src.AIGuardian.Tasks.DataStructCreate import DataStructCreate
from src.AIGuardian.Tasks.TaskRegistry import TaskRegistry

class KafkaAgent:
    def __init__(self, task_queue_topic: str=AILoggingTopics.AI_TASK_TOPIC, db_engine=None, group_id: str='default', end_processing: int=300):
        self.task_queue_topic = task_queue_topic
        self.group_id = group_id
        self.end_processing = end_processing
        self.db_engine = db_engine if db_engine else KafkaEngine.default_builder()
        self.waiting_tasks = []
        self.processed_tasks = []
        self.completed_tasks = []
        self.start_time = datetime.now()
        logging.basicConfig(
            filename=f'F:\Airflow_Test\DragonGenLogs\kafka_agent_{self.start_time.strftime("%Y_%m_%d_%H_%M_%S_%f")}.log',  # Output to file
            filemode='w',        # 'w' to overwrite, 'a' to append
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def receive_messages(self):
        
        last_consumed_records = datetime.now()
        agent_loop_cnt = 0

        while (datetime.now() - last_consumed_records).total_seconds() < self.end_processing:
            print(f"Agent Loop Count: {agent_loop_cnt} and last consumed time: {last_consumed_records}")
            agent_loop_cnt += 1
            task_queue = self.db_engine.consumers[AILoggingTopics.AI_TASK_TOPIC].poll(timeout_ms=1000, max_records=3)
            # Log records were consumed to reset timeout
            task_list = []
            for topic_partition, messages in task_queue.items():
                for message in messages:
                    if not isinstance(message.value, dict):
                        task_json = json.loads(message.value.decode('utf-8'))
                    else:
                        task_json = message.value
                    # For example, you can create an task object and execute it
                    task = TaskRegistry.build_from_json(task_json, self.db_engine)
                    # print(f"==> Task Type: {type(task)}")
                    # print(f"Task: {task.name} ==> {task.task_id} FROM ID {task_json['task_id']}")
                    task_list.append(task)
            
            # Run the task polled by the Kafka consumer
            for task_item in task_list:
                self.logger.info(f"==> Task: {task_item.name} ==> {task_item.task_id}")
                task_item.run(delay_waiting=True)
                self.processed_tasks.append(task_item)
                # Check if needs to wait
                if task_item.is_waiting():
                    self.waiting_tasks.append(task_item)
                else:
                    task_item.complete_task()
                    self.completed_tasks.append(task_item)
                    # Remove the task from the waiting list if it was added
                last_consumed_records = datetime.now()

            # Check in on waiting tasks
            if self.waiting_tasks:
                print("==> Reviewing waiting tasks")
                completed_tasks = self.db_engine.consumers[AILoggingTopics.AI_TASK_COMPLETED_TOPIC].poll(timeout_ms=1000, max_records=20)
                for task in self.waiting_tasks:
                    task.wait_on_dependency_check(completed_tasks)
                    if not task.is_waiting():
                        task.complete_task()
                        self.completed_tasks.append(task)
                        self.waiting_tasks.remove(task)
                    last_consumed_records = datetime.now()

        print("End of processing")
        self.db_engine.close()