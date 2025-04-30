import pytest
import pyodbc
import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional, Any, Union

# Import the class to be tested
from src.MetaFort.SysLogs import DatabaseConnection

# Constants for test configuration
TEST_CONNECTION_STRING = "DRIVER={SQL Server};SERVER=test_server;DATABASE=test_db;UID=test_user;PWD=test_password"

# Mock data for tests
MOCK_TABLE = "test_table"
MOCK_DATA = {"id": 1, "name": "Test", "value": 100}
MOCK_LOOKUP_KEYS = ["id"]
MOCK_LOOKUP_VALUES = [1]

@pytest.fixture
def mock_pyodbc():
    """Fixture to mock pyodbc module"""
    with patch('your_module.pyodbc') as mock:
        # Create mock connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock.connect.return_value = mock_connection
        
        # Mock datetime for consistent timestamp testing
        mock_datetime = MagicMock()
        mock_datetime.datetime.now.return_value = datetime.datetime(2025, 4, 30, 12, 0, 0)
        mock.datetime = mock_datetime
        
        yield mock

@pytest.fixture
def db_connection(mock_pyodbc):
    """Fixture for DatabaseConnection instance with mocked pyodbc"""
    connection = DatabaseConnection(TEST_CONNECTION_STRING)
    connection.connect()
    yield connection
    connection.disconnect()
