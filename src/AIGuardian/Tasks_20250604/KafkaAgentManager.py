
from kafka import KafkaProducer, KafkaConsumer
import json
from datetime import datetime
from typing import List, Dict, Any
import logging
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskState,
)

# Internal Package Imports
from src.AIGuardian.Tasks.Task import Task
from src.MetaFort.AILoggingTopics import AILoggingTopics
from src.MetaFort.SysLogs.KafkaEngine import KafkaEngine
from src.AIGuardian.Tasks.DataStructCreate import DataStructCreate
from src.AIGuardian.Tasks.TaskRegistry import TaskRegistry

class KafkaAgentManager():
    def __init__(self, task_queue_topic: str=AILoggingTopics.AI_TASK_TOPIC, db_engine=None, group_id: str='default', end_processing: int=300):
        self.task_queue_topic = task_queue_topic
        self.group_id = group_id
        self.end_processing = end_processing
        self.db_engine = db_engine if db_engine else KafkaEngine.default_builder()
        self.waiting_tasks = []
        self.start_time = datetime.now()
        self.end_time = None
        logging.basicConfig(
            filename=f'F:\Airflow_Test\DragonGenLogs\kafka_agent_{self.start_time.strftime("%Y_%m_%d_%H_%M_%S_%f")}.log',  # Output to file
            filemode='w',        # 'w' to overwrite, 'a' to append
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)

    def submit_task(self, task, user_prompt=None):
        """
        Submit a task to the Kafka topic.
        """
        # Create a task log entry
        self.db_engine.insert(topic=AILoggingTopics.AI_TASK_TOPIC, data=task.submit_task(user_prompt=user_prompt))
        self.task_log(task=task, step_status='TASK SUBMITTED')

    def wait_on_task(self, task_id, timeout=180):
        """
        Wait for the Task to complete before proceeding.
        """
        # This method should look at the completed topic for finished tasks or failed tasks.
        start_time = datetime.now()
        
        # One time use Kafka Consumer with no group_id
        temp_kc = KafkaConsumer(
                    AILoggingTopics.AI_TASK_COMPLETED_TOPIC,
                    bootstrap_servers=[self.db_engine.connection_string],
                    auto_offset_reset='latest')

        task_completed = False
        output_params = {}
        while not task_completed and (datetime.now() - start_time).total_seconds() < timeout:
            completed_tasks = temp_kc.poll(timeout_ms=1000, max_records=10)
            completed_tasks_list = self.kafka_records_to_list(completed_tasks, key='task_id')
            completed_tasks_dict = self.kafka_records_to_dict(completed_tasks, key='task_id', val='output_artifacts')
            if task_id in completed_tasks_list:
                task_completed = True
                print(f"==> Task {task_id} completed.")
                return completed_tasks_dict.get(task_id)

    def task_log(self, task, task_state=TaskState.working, step_status=None, error_code=None, error_message=None):
        """
        Log the task to the database.
        """
        # Create a task log entry
        task_log_entry = task.update_task_log(task_state, step_status, error_code, error_message)
        self.db_engine.insert(topic=AILoggingTopics.AI_TASK_LOG_TOPIC, data=task_log_entry)

    def receive_messages(self):
        
        last_consumed_records = datetime.now()
        agent_loop_cnt = 0

        while (datetime.now() - last_consumed_records).total_seconds() < self.end_processing:
            print(f"Agent Loop Count: {agent_loop_cnt} and last consumed time: {last_consumed_records}")
            agent_loop_cnt += 1
            # Grab records from the Kafka topic (This is under the universal consumer group_id = action-agent)
            task_queue = self.db_engine.consumers[AILoggingTopics.AI_TASK_TOPIC].poll(timeout_ms=1000, max_records=3)
            task_list = []
            for topic_partition, messages in task_queue.items():
                for message in messages:
                    # TODO move decoding to the KafkaEngine
                    if not isinstance(message.value, dict):
                        task_json = json.loads(message.value.decode('utf-8'))
                    else:
                        task_json = message.value
                    # For example, you can create an task object and execute it
                    # TODO add try-except around construction of the task object
                    task = TaskRegistry.build_from_json(task_json, self.db_engine)
                    self.task_log(task=task, step_status='TASK PICKED UP')
                    task_list.append(task)
            
            # Run the task polled by the Kafka consumer
            for task_item in task_list:
                self.logger.info(f"==> Task: {task_item.name} ==> {task_item.task_id}")
                print(f"==> Task: {task_item.name} ==> {task_item.task_id}")
                self.task_log(task=task_item, step_status='TASK RUNNING')
                task_item.run()
                self.task_log(task=task_item, step_status='TASK RUNNING DONE')
                print(task_item.response)
                # try:
                #     self.task_log(task=task_item, step_status='TASK RUNNING')
                #     task_item.run()
                #     self.task_log(task=task_item, step_status='TASK RUNNING DONE')
                #     print(task_item.response)
                # except Exception as e:
                #     self.task_log(task=task_item, step_status='TASK RUNNING ERROR', error_code=str(e), error_message=str(e))
                #     print(f"Error: {e}")
                #     continue
                # Submit any generated tasks
                if isinstance(task_item.response, list):
                    for generated_task in task_item.response:
                        self.submit_task(generated_task)
                # Check if needs to wait
                if task_item.is_waiting():
                    self.waiting_tasks.append(task_item)
                    self.task_log(task=task_item, step_status='TASK WAITING')
                else:
                    data = task_item.complete_task()
                    self.db_engine.insert(topic=AILoggingTopics.AI_TASK_COMPLETED_TOPIC, data=data)
                    self.task_log(task=task_item, step_status='TASK COMPLETED')
                last_consumed_records = datetime.now()

            # Check in on waiting tasks
            if self.waiting_tasks:
                completed_tasks = self.db_engine.consumers[AILoggingTopics.AI_TASK_COMPLETED_TOPIC].poll(timeout_ms=1000, max_records=20)
                completed_tasks_json = self.kafka_records_to_list(completed_tasks, key='ALL')
                tasks_to_remove = []
                for task in self.waiting_tasks:
                    task.process_dependency_check(completed_tasks_json)
                    if not task.is_waiting():
                        data = task.complete_task()
                        self.db_engine.insert(topic=AILoggingTopics.AI_TASK_COMPLETED_TOPIC, data=data)
                        tasks_to_remove.append(task)
                        self.task_log(task=task_item, step_status='TASK COMPLETED')
                        last_consumed_records = datetime.now()
                # Remove the completed task after interating through it
                for r_task in tasks_to_remove:
                    self.waiting_tasks.remove(r_task)

        print("End of processing")
        self.end_time = datetime.now()
        # self.db_engine.close()

    # TODO move this to the KafkaEngine
    def kafka_records_to_list(self, records, key):
        kcr_list = []
        for topic_partition, c_messages in records.items():
            for c_message in c_messages:
                if not isinstance(c_message.value, dict):
                    task_json = json.loads(c_message.value.decode('utf-8'))
                else:
                    task_json = c_message.value
                # Allow for the user to specify a key or ALL to get the whole dictionary message
                if key == 'ALL':
                    kcr_list.append(task_json)
                else:
                    kcr_list.append(task_json.get(key))
        return kcr_list
    
    # TODO move this to the KafkaEngine
    def kafka_records_to_dict(self, records, key, val):
        kcr_dict = {}
        for topic_partition, c_messages in records.items():
            for c_message in c_messages:
                if not isinstance(c_message.value, dict):
                    task_json = json.loads(c_message.value.decode('utf-8'))
                else:
                    task_json = c_message.value
                # Allow for the user to specify a key or ALL to get the whole dictionary message
                if val == 'ALL':
                    kcr_dict[task_json.get(key)] = task_json
                else:
                    kcr_dict[task_json.get(key)] = task_json.get(val)
        return kcr_dict