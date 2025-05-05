import json
from ..ActionsFrame.Action import Action
from ..ActionGenerator.ColumnRefiner import ColumnRefiner


class ActionGenerator(Action):
    def __init__(self, input_params=None, sequence_limit=10, verbose=False, parent_action=None):
        super().__init__(input_params, sequence_limit, verbose, parent_action)

    # region static variables
    @staticmethod
    def get_description():
        return """Create a set of sub-actions to be run."""
    
    @staticmethod
    def get_action_type():
        return 'Generator'
    
    @staticmethod
    def get_action_version():
        return '0.0.1'

    @staticmethod
    def get_system_prompt():
        return None # This does not call the AI APIs, so None will indicate this for the system.
    
    # endregion static variables
    
    def get_output_params_struct(self):
        """
        A representtation of the output coming from this step. (output_type, output_struct_str)
        """
        # This method should be overridden in subclasses to provide specific output parameters
        return {
            "output_type": GenAIUtils.valid_output_type("ActionList"),
            "output_struct": [],
        }
    
    # region Action Methods
    def engineer_prompt(self, user_prompt):
        """
        Generate a prompt for the action based on the user input.
        """
        # This method should be overridden in subclasses to provide specific prompts
        raise Exception(f"This function should not be called for {__class__.__name__} class types, because they do not call AI!")
    
    def get_messages(self):
        """
        Get the messages for the action.
        """
        # This method should be overridden in subclasses to provide specific messages
        raise Exception("This function should not be called for {__class__.__name__} class types, because they do not call AI!")
    
    def validate_parameters(self, parameters):
        """
        Validate the parameters for the action.
        """
        # This method should be overridden in subclasses to provide specific validation
         # Reserved parameters for the actions
            # ai_tools -> used for feeding to the AI to potentially use.
            # rag_objects -> used for potentially pulling or pushing to the AI.
        return True
    
    def hygiene_output(self, text_response):
        """
        Clean the output of the action.
        """
        # This method should be overridden in subclasses to provide specific cleaning
        return text_response
    
    def validate_output(self, text_response):
        """
        Validate the output of the action.
        """
        # This method should be overridden in subclasses to provide specific validation
        self.text_response = text_response
        return True
    
    @record_step("COMPLETED")
    def complete_action(self):
        """
        Complete the action based of the values from the AI gnerated response. Fill in the output_params for the action.
        """
        # This method should be overridden in subclasses to provide specific completion actions
        self.is_completed = True

    def next_action(self):
        """
        Choose the next action based on the current action.
        """
        # This method should be overridden in subclasses to provide specific next actions
        self.child_action = [] if self.child_action is None else self.child_action
        return self.child_action
    
    def geneterate_actions(self):
        """
        Generate actions based on the schema.
        """
        self.child_action = [] if self.child_action is None else self.child_action
        return self.child_action

    def run(self, user_prompt):
        """
        Run the code to generate schema refinement actions.
        """
        if self._step_name_code < 100:
            self.initialize()
        for action in self.geneterate_actions():
            user_prompt = self.parent_action.user_prompt if self.parent_action else ""
            action.run(user_prompt)

    # endregion Action Methods
