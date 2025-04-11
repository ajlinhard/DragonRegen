
class FromDataSingleton(type):
    """
    Singleton metaclass for the FromData class.
    This metaclass ensures that only one instance of the FromData class is created.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        # Check if the singleton data class is already instantiated.
        if cls not in cls._instances:
            # Create and store the instance if it doesn't exist, using the type __call__ method.
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

    @staticmethod
    def cleanup(cls):
        """
        Cleanup method to remove the singleton instance.
        This is useful for testing purposes to ensure a fresh instance can be created.
        """
        if cls in cls._instances:
            del cls._instances[cls]