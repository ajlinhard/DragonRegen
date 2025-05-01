import pyodbc
import datetime
import json
from typing import Dict, List, Optional, Any, Union

class DatabaseEngine:
    """Base class for database connection handling"""
    d_log_tables = {"dyn_sql_execution_log": {
    "purpose": "Track the execution of dynamic SQL commands",
    "fields": [
      {"name": "execution_id", "type": "Integer", "nullable": False, "metadata": {"description": "Primary key, unique identifier for the execution"}},
      {"name": "sql_command", "type": "String", "nullable": False, "metadata": {"description": "The SQL command that was executed"}},
      {"name": "sql_params", "type": "String", "nullable": False, "metadata": {"description": "The list of parameters used to replace the placeholders in the SQL command"}},
      {"name": "start_time", "type": "String", "nullable": False, "metadata": {"description": "Timestamp when the command was executed"}},
      {"name": "stop_time", "type": "String", "nullable": False, "metadata": {"description": "Timestamp when the command was executed"}},
      {"name": "status", "type": "String", "nullable": False, "metadata": {"description": "Status of the execution (success, failure)"}},
      {"name": "user_name", "type": "String", "nullable": False, "metadata": {"description": "Error message if execution failed"}},
      {"name": "process_id", "type": "String", "nullable": False, "metadata": {"description": "Processing ID initiation time. This plus Process ID should be unique on the server/system."}},
      {"name": "process_login_time", "type": "Timestamp", "nullable": False, "metadata": {"description": "Processing ID of the execution"}},
      {"name": "error_message", "type": "String", "nullable": True, "metadata": {"description": "Error message if execution failed"}},
      {"name": "error_timestamp", "type": "String", "nullable": True, "metadata": {"description": "When the error occurred"}},
      {"name": "metadata", "type": "JSON", "nullable": True,  # Assuming JSON is a valid type in your database
      	"metadata": {"description":"JSON field for any additional metadata related to the execution"}}
    ]
    }}
    
    def __init__(self, connection_string: str, autocommit: bool = True, b_debug: bool = False):
        """Initialize database connection
        
        Args:
            connection_string: Connection string for the database
        """
        self.connection_string = connection_string
        self.autocommit = autocommit
        self.b_debug = b_debug
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database"""
        try:
            self.connection = pyodbc.connect(self.connection_string, autocommit=self.autocommit)
            self.cursor = self.connection.cursor()
            return True
        except pyodbc.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def commit(self):
        """Commit the current transaction"""
        if self.connection:
            self.connection.commit()
    
    def rollback(self):
        """Rollback the current transaction"""
        if self.connection:
            self.connection.rollback()

    def log_execution(self, sql: str, params: Optional[Union[Dict[str, Any], List[Any]]], 
                      stats: dict, start_time: datetime.datetime, stop_time: datetime.datetime):
        """Log the execution of a SQL command
        
        Args:
            sql: SQL command that was executed
            params: Parameters used in the SQL command
            stats: Statistics about the execution (e.g., row count)
            start_time: Start time of the execution
            stop_time: Stop time of the execution
        """
        # TODO: (option) to add this execution with the incoming sql using cursor.executemany(), but need to confirm what happens on error mid iteration.
        log_sql = f"""
            INSERT INTO dyn_sql_execution_log 
            (sql_command, sql_params, start_time, stop_time, status, user_name, process_id, process_login_time, error_message, error_timestamp, metadata)
            VALUES (?, ?, ?, ?, ?
                , {self.user_name_str()}
                , {self.process_id_str()}
                , {self.process_login_time_str()}
                , ?, ?, ?)
        """
        log_params = (sql
                  , str(params)
                  , start_time
                  , stop_time
                  , stats.get("status", "SUCCESS")
                  , stats.get("error_message", "null")
                  , stats.get("error_timestamp", "null")
                  , json.dumps(stats.get("metadata", "null"))
                )
        try:
            if self.b_debug: print(log_sql)
            self.cursor.execute(log_sql, log_params)
            self.commit()
        except pyodbc.Error as e:
            print(f"Error logging SQL execution: {e}")
            self.rollback()
    # region: built-in functions for db engine
    def user_name_str(self):
        """Get the user name string for logging"""
        return "suser_name()"
    
    def process_login_time_str(self):
        """Get the session ID string for logging"""
        return "(select login_time from sys.dm_exec_sessions where session_id = @@SPID)"
    
    def process_id_str(self):
        """Get the session ID string for logging"""
        return "@@SPID"
    # endregion
    

    def execute_w_logging(self, sql: str, params: Optional[Union[Dict[str, Any], List[Any]]] = None, fetch_row_count: int=None) -> dict:
        """Execute a SQL command with logging
        
        Args:
            sql: SQL command to execute
            params: Parameters for the SQL command
            fetch_row_count: Number of rows to fetch (if applicable)
        
        Returns:
            Dictionary containing the result of the SQL command
        """
        results = None
        stats = {}
        try:
            start_time = datetime.datetime.now()
            if self.b_debug: print(f"Executing SQL: {sql} with params: {params}")
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            stats['status'] = "SUCCESS"
            stop_time = datetime.datetime.now()
            
            if fetch_row_count is not None:
                rows = self.cursor.fetchmany(fetch_row_count)
                stats['status'] = "SUCCESS"
                stats['metadata'] = {"rows": rows, "row_count": len(rows)}
                results = dict(zip([column[0] for column in self.cursor.description], rows))
            else:
                stats['metadata'] = {"row_count": self.cursor.rowcount}
        except pyodbc.Error as e:
            print(f"Error executing SQL: {e}")
            stats['status'] = "FAILED"
            stop_time = datetime.datetime.now()
            raise e
        finally:
            self.log_execution(sql, params, stats, start_time, stop_time)
        return results

    def upsert(self, table: str, data: Dict[str, Any], lookup_keys: List[str] = None) -> bool:
        """Upsert data into the database
        
        Args:
            table: Name of the table to upsert data into
            data: Dictionary of column names and values to upsert
            lookup_keys: List of column names to use as lookup keys for the upsert
        
        Returns:
            True if the upsert was successful, False otherwise
        """
        if lookup_keys is None:
            raise ValueError("Lookup keys must be provided for upsert operation")
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        update_set = ', '.join([f"{key} = ?" for key in data.keys()])
        
        conditions = ' AND '.join([f"{key} = ?" for key in lookup_keys])
        sql = f"""
            MERGE INTO {table} AS target
            USING (SELECT {placeholders}) AS source ({columns})
            ON {conditions}
            WHEN MATCHED THEN
                UPDATE SET {update_set}
            WHEN NOT MATCHED THEN
                INSERT ({columns}) VALUES ({placeholders});
        """
        
        try:
            self.cursor.execute(sql, tuple(data.values()) + tuple(data.values()))
            self.commit()
            return True
        except pyodbc.Error as e:
            print(f"Error upserting data: {e}")
            self.rollback()
            return False

    def insert(self, table: str, data: Dict[str, Any]) -> bool:
        """Insert data into the database
        
        Args:
            table: Name of the table to insert data into
            data: Dictionary of column names and values to insert
        
        Returns:
            True if the insert was successful, False otherwise
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"""INSERT INTO {table} ({columns}) VALUES ({placeholders})
        SELECT SCOPE_IDENTITY();
        """
        
        try:
            self.cursor.execute(sql, tuple(data.values()))
            identity_value = self.cursor.fetchval()
            self.commit()
            return identity_value
        except pyodbc.Error as e:
            print(f"Error inserting data: {e}")
            self.rollback()
            return None
        
    def select_lookup(self, table: str, lookup_keys: List[str], lookup_values: List[Any]) -> Optional[Dict[str, Any]]:
        """Select data from the database based on lookup keys
        
        Args:
            table: Name of the table to select data from
            lookup_keys: List of column names to use as lookup keys
            lookup_values: List of values to use for the lookup
        
        Returns:
            Dictionary of selected data or None if no data was found
        """
        if len(lookup_keys) != len(lookup_values):
            raise ValueError("Number of lookup keys must match number of lookup values")
        
        conditions = ' AND '.join([f"{key} = ?" for key in lookup_keys])
        sql = f"SELECT * FROM {table} WHERE {conditions}"
        
        try:
            self.cursor.execute(sql, tuple(lookup_values))
            row = self.cursor.fetchone()
            if row:
                return dict(zip([column[0] for column in self.cursor.description], row))
            else:
                return None
        except pyodbc.Error as e:
            print(f"Error selecting data: {e}")
            return None
        
    def create_table(self, table_name, schema):
        """
        Create a table in Spark with the given name and schema.
        """
        # Check if the schema is a string or StructType
        if isinstance(schema, str):
            pass  # Assuming schema is a SQL string, no need to create an empty DataFrame
        # elif isinstance(schema, StructType):
        #     schema = SchemaMSSQL.generate_schema_sql(json.loads(schema.json()))
        else:
            raise ValueError(f"Schema should be a string or StructType, but was {type(schema)}")
        
        s_create_table = f"""if OBJECT_ID('dbo.{table_name}', 'U') IS NULL
        CREATE TABLE dbo.{table_name} 
        ({schema})
        ;"""
        self.execute_w_logging(s_create_table)
        return f"Table {table_name} created with schema: {schema}"