import pytest
from DataCreator.DataGenerators.FromDataSingleton import FromDataSingleton


@pytest.fixture(scope="class")
def cleanup_singleton():
    """
    During testing the singleton instance is removed to allow for re-initialization based testing.
    This is especially, important when running with the other test modules.
    """
    # Remove the singleton instance if it exists
    return FromDataSingleton.cleanup