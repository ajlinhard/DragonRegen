
class ColGenRegistry():
    """
    Registry for column generators.
    """
    _registry = {}

    @classmethod
    def add_registry(cls, col_type):
        """
        Create a decorator for registering column generators.
        """
        def decorator(subclass):
            cls._registry[col_type] = subclass
            return subclass
        return decorator
    
    @classmethod
    def get_col_generator(cls, col_type):
        """
        Get a column generator by type.
        """
        return cls._registry.get(col_type, None)
    
    @classmethod
    def get_all_descriptions(cls):
        """
        Get all descriptions of the column generators.
        """
        return {col_type: generator.get_description() for col_type, generator in ColGenRegistry._registry.items()}