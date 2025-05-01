from abc import ABC, abstractmethod
import datetime
from ...MetaFort.SysLogs.DatabaseEngine import DatabaseEngine

class Action():
    _registry = {}

    def __init__(self, db_engine, parameters=None):
        self.db_engine = db_engine
        self.parameters = parameters
        # action tree variables and identifiers
        self.action_id = None
        self.group_action_id = None
        self.sequence = 0
        self.prompt = None
        self.response = None
        self.ls_next_actions = []
        self.parent_action = None
        # read-only properties
        self._name = self.__class__.__name__
        self._description = Action.get_description()
        self._action_type = Action.get_action_type()
        self._action_version = Action.get_action_version()
        self._system_prompt = Action.get_system_prompt()
        self._status = 'INITIALIZED'
        self.set_action_id()

    @classmethod
    def register(cls, action_name):
        def decorator(subclass):
            cls._registry[action_name] = subclass
            return subclass
        return decorator

    @classmethod
    def from_parent_action(cls, parent_action):
        """
        Create a new action from a parent action.
        """
        new_action = cls(
            db_engine=parent_action.db_engine,
            parameters=cls.potential_parameters(parent_action.parameters),
        )
        new_action.parent_action = parent_action
        new_action.group_action_id = parent_action.action_id
        new_action.sequence = parent_action.sequence + 1
        new_action.set_action_id()
        return new_action

    # region static variables
    @staticmethod
    @abstractmethod
    def get_description():
        return 'The base action class. This should be inherited by all action classes.'
    
    @staticmethod
    @abstractmethod
    def get_action_type():
        return 'base_action'
    
    @staticmethod
    @abstractmethod
    def get_action_version():
        return '0.0.1'

    @staticmethod
    @abstractmethod
    def get_system_prompt():
        return """This is the system prompt for the base action."""
    
    # endregion static variables

    @staticmethod
    @abstractmethod
    def potential_parameters(parameters):
        """
        Generate potential parameters for the action.
        """
        # This method should be overridden in subclasses to provide specific parameters

        return parameters
    
    @abstractmethod
    def next_actions(self):
        """
        Get the next actions based on the current action.
        """
        # This method should be overridden in subclasses to provide specific next actions
        return self.ls_next_actions

    
    # region Properties
    @property
    def name(self):
        return self._name
    
    @property
    def description(self):
        return self._description
    
    @property
    def action_type(self):
        return self._action_type
    
    @property
    def action_version(self):
        return self._action_version
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value

    # endregion Properties

    # region setup methods
    def set_action_id(self):
        """
        Get the action ID.
        """
        if self.action_id is None:
            # put or pull from the database
            table = 'actions'
            data_row = {"action_name": self.name,
                "action_version": self.action_version,
                "parent_action_id": self.parent_action.action_id if self.parent_action else None,
                "group_action_id": self.group_action_id,
                "description": self.description,
                "sequence": self.sequence,
                "created_dt": datetime.datetime.now(),
                "updated_dt": datetime.datetime.now(),
                "status": self.status,
                "metadata": self.parameters,
            }
            self.action_id = self.db_engine.insert(table=table, data=data_row)
            if self.group_action_id is None:
                self.group_action_id = self.action_id
            # self.db_engine.update(table=table, data={"updated_dt": datetime.datetime.now()}, where={"action_id": self.action_id})
        return self.action_id
    
    # endregion setup methods

    @abstractmethod
    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the action based on the user input.
        """
        # This method should be overridden in subclasses to provide specific prompts
        return user_prompt
    

    @abstractmethod
    def generate_action(self, user_prompt):
        """
        Generate an action based on the user input.
        """
        # This method should be overridden in subclasses to provide specific actions
        return self.engineer_prompt(user_prompt)
    
    @abstractmethod
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the action.
        """
        # This method should be overridden in subclasses to provide specific validation
        return True
    
    @abstractmethod
    def validate_output(self, output):
        """
        Validate the output of the action.
        """
        # This method should be overridden in subclasses to provide specific validation
        return True
    
    def log_action(self):
        """
        Log the actions to the database. Included the request table.
        """
        # log the request

        # log the action completed or failed

    @abstractmethod
    def complete_action(self):
        """
        Complete the action based of the values from the AI gnerated response.
        """
        # This method should be overridden in subclasses to provide specific completion actions
        self.log_action()
        return self.action_id

    @abstractmethod
    def next_action(self):
        """
        Choose the next action based on the current action.
        """
        # This method should be overridden in subclasses to provide specific next actions
        return self.ls_next_actions
