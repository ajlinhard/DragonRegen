from abc import ABC, abstractmethod
import datetime
import json
from ...MetaFort.AILoggingTables import AILoggingTables

class Action(ABC):
    _registry = {}

    def __init__(self, parameters=None):
        self.parameters = parameters
        # action tree variables and identifiers
        self.action_id = None
        self.group_action_id = None
        self.sequence = 0
        self.user_prompt = None
        self.engineered_prompt = None
        self.response = None
        self.parent_action = None
        # read-only properties
        self._name = self.__class__.__name__
        self._description = Action.get_description()
        self._action_type = Action.get_action_type()
        self._action_version = Action.get_action_version()
        self._system_prompt = Action.get_system_prompt()
        self.model_parameters = {"max_tokens": 2000,
            "temperature": 0.1,
            "stop_sequences": ["}"],
            "pref_model_type": "COMPLEX",
            "ai_tools": self.get_tools(),
        }
        self._status = 'INITIALIZED'
        
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

    def set_action_id(self, action_id=None):
        self.action_id = action_id
        if self.group_action_id is None:
                self.group_action_id = self.action_id

    # endregion Properties

    @abstractmethod
    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the action based on the user input.
        """
        # This method should be overridden in subclasses to provide specific prompts
        self.user_prompt = user_prompt
        self.engineered_prompt = user_prompt
        return self.engineered_prompt
    
    @abstractmethod
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the action.
        """
        # This method should be overridden in subclasses to provide specific validation
         # Reserved parameters for the actions
            # ai_tools -> used for feeding to the AI to potentially use.
            # rag_objects -> used for potentially pulling or pushing to the AI.
        return True
    
    @abstractmethod
    def hygiene_output(self, text_response):
        """
        Clean the output of the action.
        """
        # This method should be overridden in subclasses to provide specific cleaning
        return text_response
    
    @abstractmethod
    def validate_output(self, output):
        """
        Validate the output of the action.
        """
        # This method should be overridden in subclasses to provide specific validation
        return True
    
    @abstractmethod
    def complete_action(self):
        """
        Complete the action based of the values from the AI gnerated response.
        """
        # This method should be overridden in subclasses to provide specific completion actions
        pass

    @abstractmethod
    def next_action(self):
        """
        Choose the next action based on the current action.
        """
        # This method should be overridden in subclasses to provide specific next actions
        return None
    
    def get_tools(self):
        """
        Get the tools for this action class or utility classes for the AI to consider using.
        """
        # This method should be overridden in subclasses to provide specific tools
        return None
