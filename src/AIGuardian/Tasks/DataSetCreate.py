
import os
import json
from a2a.types import (
    AgentAuthentication,
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskState,
)
from pydantic import BaseModel
from pyspark.sql import SparkSession
from pyspark.sql.types import *

from src.AIGuardian.Tasks.Task import Task
from src.AIGuardian.Tasks.TaskGenerator import TaskGenerator
from src.AIGuardian.Tasks.ColumnRefiner import ColumnRefiner
from src.AIGuardian.AIUtils import GenAIUtils
from src.AIGuardian.Tasks.TaskRegistry import TaskRegistry
from src.DataCreator.DataSets.DataSetGenStandard import DataSetGenStandard
from src.DataCreator.SchemaGenerators.SchemaSpark import SchemaSpark
from src.DataCreator.DataGenerators.FirstNameData import FirstNameData
from src.DataCreator.DataGenerators.LastNameData import LastNameData

class DataSetCreateInput(BaseModel):
    """
    Represents the input parameters for the DataSetCreate task.
    """
    schema_list: list[dict] = []
    creation_engine: str = "spark"
    output_location: str = "data/output"
    output_format: str = "parquet"


@TaskRegistry.register("SchemaRefiner")
class DataSetCreate(TaskGenerator):
    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_task=None):
        super().__init__(input_params, sequence_limit, verbose, parent_task)

    # region static variables
    @staticmethod
    def get_description():
        return """Create a set of sub-tasks to refine the schema with more details."""
    
    @staticmethod
    def get_task_type():
        return 'schema'
    
    @staticmethod
    def get_task_version():
        return '0.0.1'

    # endregion static variables
    
    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return {
            "output_type": GenAIUtils.valid_output_type("taskList"),
            "output_struct": [ColumnRefiner],
        }
    
    def setup_input_params(self):
        """
        Setup the input parameters for the Task. Sometimes it will be mined or pulled from parent Tasks.
        """
        # Check if the input_params is a file path
        if isinstance(self.input_params, str):
            # Check if the file exists
            if not os.path.isfile(self.input_params):
                raise ValueError(f"Input parameters file does not exist: {self.input_params}")
            try:
                with open(self.input_params, 'r') as file:
                    self.input_params = json.load(file)
            except FileNotFoundError:
                raise ValueError(f"File not found: {self.input_params}")
            except json.JSONDecodeError:
                raise ValueError(f"Invalid JSON format in file: {self.input_params}")
        else:
            super().setup_input_params()

    # region task Methods
    def geneterate_tasks(self):
        """
        Generate tasks based on the schema.
        """
        return None
    
    def complete_task(self):
        # Loop through the child tasks and rebuild the schema.
        sturct_col = SchemaSpark.generate_schema(self.input_params)

        # Create Spark Engine
        spark = SparkSession.builder \
            .appName("Test Data Set Generation") \
            .enableHiveSupport() \
            .master("local[*]") \
            .getOrCreate()
        
        # Add method for detecting if any name fields are present in the schema
        FirstNameGen = FirstNameData(spark)
        LastNameGen = LastNameData(spark)

        df_list = {}
        # Generate the dataset
        for schema_name, schema in sturct_col.items():
            data_gen = DataSetGenStandard(spark, schema, 100)
            # Generate the DataFrame
            # TODO: maybe have the generator detect or see and attribute that is labeled as DataFrame/appended to the schema
            df = data_gen.generate_data()

        return super().complete_task()

    # region task Methods
