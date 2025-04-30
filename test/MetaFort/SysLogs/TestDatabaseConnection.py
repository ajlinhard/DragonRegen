import pytest
import pyodbc
import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Optional, Any, Union

# Import the class to be tested
from src.MetaFort.SysLogs.DatabaseEngine import DatabaseEngine

class TestDatabaseEngine:
    """Test cases for DatabaseEngine class"""
    
    def test_initialization(self):
        """Test initialization of DatabaseEngine"""
        connection = DatabaseEngine(TEST_CONNECTION_STRING)
        assert connection.connection_string == TEST_CONNECTION_STRING
        assert connection.autocommit is True
        assert connection.connection is None
        assert connection.cursor is None
        
        # Test with custom autocommit
        connection = DatabaseEngine(TEST_CONNECTION_STRING, autocommit=False)
        assert connection.autocommit is False
    
    def test_connect(self, mock_pyodbc):
        """Test connect method"""
        connection = DatabaseEngine(TEST_CONNECTION_STRING)
        result = connection.connect()
        
        assert result is True
        mock_pyodbc.connect.assert_called_once_with(TEST_CONNECTION_STRING, autocommit=True)
        assert connection.connection is not None
        assert connection.cursor is not None
    
    def test_connect_failure(self, mock_pyodbc):
        """Test connect method when connection fails"""
        mock_pyodbc.connect.side_effect = pyodbc.Error("Connection failed")
        connection = DatabaseEngine(TEST_CONNECTION_STRING)
        result = connection.connect()
        
        assert result is False
        assert connection.connection is None
        assert connection.cursor is None
    
    def test_disconnect(self, db_connection, mock_pyodbc):
        """Test disconnect method"""
        db_connection.disconnect()
        
        db_connection.cursor.close.assert_called_once()
        db_connection.connection.close.assert_called_once()
    
    def test_commit(self, db_connection):
        """Test commit method"""
        db_connection.commit()
        db_connection.connection.commit.assert_called_once()
    
    def test_rollback(self, db_connection):
        """Test rollback method"""
        db_connection.rollback()
        db_connection.connection.rollback.assert_called_once()
    
    def test_user_name_str(self, db_connection):
        """Test user_name_str method"""
        assert db_connection.user_name_str() == "suser_name()"
    
    def test_process_login_time_str(self, db_connection):
        """Test process_login_time_str method"""
        assert db_connection.process_login_time_str() == "(select login_time from sys.dm_exec_sessions where session_id = @@SPID)"
    
    def test_process_id_str(self, db_connection):
        """Test process_id_str method"""
        assert db_connection.process_id_str() == "@@SPID"
    
    def test_log_execution(self, db_connection, mock_pyodbc):
        """Test log_execution method"""
        # Setup test data
        sql = "SELECT * FROM test_table"
        params = {"id": 1}
        stats = {"status": "SUCCESS", "metadata": {"row_count": 1}}
        start_time = datetime.datetime(2025, 4, 30, 11, 0, 0)
        stop_time = datetime.datetime(2025, 4, 30, 11, 0, 1)
        
        # Call method
        db_connection.log_execution(sql, params, stats, start_time, stop_time)
        
        # Assert cursor.execute was called with the correct SQL and parameters
        db_connection.cursor.execute.assert_called_once()
        # Check that commit was called
        db_connection.connection.commit.assert_called_once()
    
    def test_log_execution_failure(self, db_connection, mock_pyodbc):
        """Test log_execution method when there's an error"""
        # Setup test data
        sql = "SELECT * FROM test_table"
        params = {"id": 1}
        stats = {"status": "SUCCESS"}
        start_time = datetime.datetime(2025, 4, 30, 11, 0, 0)
        stop_time = datetime.datetime(2025, 4, 30, 11, 0, 1)
        
        # Make cursor.execute raise an exception
        db_connection.cursor.execute.side_effect = pyodbc.Error("Execution failed")
        
        # Call method
        db_connection.log_execution(sql, params, stats, start_time, stop_time)
        
        # Check that rollback was called
        db_connection.connection.rollback.assert_called_once()
    
    def test_execute_w_logging_success(self, db_connection, mock_pyodbc):
        """Test execute_w_logging method with successful execution"""
        # Setup mock cursor
        db_connection.cursor.description = [("id",), ("name",)]
        db_connection.cursor.fetchmany.return_value = [(1, "Test")]
        
        # Call method
        result = db_connection.execute_w_logging("SELECT * FROM test_table", fetch_row_count=1)
        
        # Assert cursor.execute was called
        db_connection.cursor.execute.assert_called_once_with("SELECT * FROM test_table")
        # Assert log_execution was called
        assert isinstance(result, dict)
    
    def test_execute_w_logging_with_params(self, db_connection):
        """Test execute_w_logging method with parameters"""
        # Setup params
        params = [1, "Test"]
        
        # Call method
        db_connection.execute_w_logging("SELECT * FROM test_table WHERE id = ? AND name = ?", params)
        
        # Assert cursor.execute was called with params
        db_connection.cursor.execute.assert_called_once_with(
            "SELECT * FROM test_table WHERE id = ? AND name = ?", params
        )
    
    def test_execute_w_logging_failure(self, db_connection):
        """Test execute_w_logging method with execution failure"""
        # Make cursor.execute raise an exception
        db_connection.cursor.execute.side_effect = pyodbc.Error("Execution failed")
        
        # Call method and expect exception
        with pytest.raises(pyodbc.Error):
            db_connection.execute_w_logging("SELECT * FROM test_table")
    
    def test_upsert_success(self, db_connection):
        """Test upsert method with successful execution"""
        # Call method
        result = db_connection.upsert(MOCK_TABLE, MOCK_DATA, MOCK_LOOKUP_KEYS)
        
        # Assert cursor.execute was called
        db_connection.cursor.execute.assert_called_once()
        # Assert commit was called
        db_connection.connection.commit.assert_called_once()
        assert result is True
    
    def test_upsert_without_lookup_keys(self, db_connection):
        """Test upsert method without lookup keys"""
        # Call method and expect exception
        with pytest.raises(ValueError):
            db_connection.upsert(MOCK_TABLE, MOCK_DATA)
    
    def test_upsert_failure(self, db_connection):
        """Test upsert method with execution failure"""
        # Make cursor.execute raise an exception
        db_connection.cursor.execute.side_effect = pyodbc.Error("Upsert failed")
        
        # Call method
        result = db_connection.upsert(MOCK_TABLE, MOCK_DATA, MOCK_LOOKUP_KEYS)
        
        # Assert rollback was called
        db_connection.connection.rollback.assert_called_once()
        assert result is False
    
    def test_insert_success(self, db_connection):
        """Test insert method with successful execution"""
        # Call method
        result = db_connection.insert(MOCK_TABLE, MOCK_DATA)
        
        # Assert cursor.execute was called
        db_connection.cursor.execute.assert_called_once()
        # Assert commit was called
        db_connection.connection.commit.assert_called_once()
        assert result is True
    
    def test_insert_failure(self, db_connection):
        """Test insert method with execution failure"""
        # Make cursor.execute raise an exception
        db_connection.cursor.execute.side_effect = pyodbc.Error("Insert failed")
        
        # Call method
        result = db_connection.insert(MOCK_TABLE, MOCK_DATA)
        
        # Assert rollback was called
        db_connection.connection.rollback.assert_called_once()
        assert result is False
    
    def test_select_lookup_success(self, db_connection):
        """Test select_lookup method with successful execution"""
        # Setup mock cursor
        db_connection.cursor.description = [("id",), ("name",), ("value",)]
        db_connection.cursor.fetchone.return_value = (1, "Test", 100)
        
        # Call method
        result = db_connection.select_lookup(MOCK_TABLE, MOCK_LOOKUP_KEYS, MOCK_LOOKUP_VALUES)
        
        # Assert cursor.execute was called
        db_connection.cursor.execute.assert_called_once()
        assert isinstance(result, dict)
        assert result["id"] == 1
        assert result["name"] == "Test"
        assert result["value"] == 100
    
    def test_select_lookup_no_result(self, db_connection):
        """Test select_lookup method with no results"""
        # Setup mock cursor to return None
        db_connection.cursor.fetchone.return_value = None
        
        # Call method
        result = db_connection.select_lookup(MOCK_TABLE, MOCK_LOOKUP_KEYS, MOCK_LOOKUP_VALUES)
        
        # Assert result is None
        assert result is None
    
    def test_select_lookup_mismatched_keys_and_values(self, db_connection):
        """Test select_lookup method with mismatched keys and values"""
        # Call method with mismatched keys and values
        with pytest.raises(ValueError):
            db_connection.select_lookup(MOCK_TABLE, ["id", "name"], [1])
    
    def test_select_lookup_failure(self, db_connection):
        """Test select_lookup method with execution failure"""
        # Make cursor.execute raise an exception
        db_connection.cursor.execute.side_effect = pyodbc.Error("Select failed")
        
        # Call method
        result = db_connection.select_lookup(MOCK_TABLE, MOCK_LOOKUP_KEYS, MOCK_LOOKUP_VALUES)
        
        # Assert result is None
        assert result is None