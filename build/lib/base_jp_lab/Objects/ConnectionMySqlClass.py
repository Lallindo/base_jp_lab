import mysql.connector
import mysql.connector.pooling
from mysql.connector import Error, InterfaceError
import time
from typing import Optional

class ConnectionMySql():
    """Enhanced MySQL connection class with robust error handling"""
    
    _connection_pool = None
    _pool_initialized = False
    
    def __init__(self, user: str, password: str, host: str, port: str, name: str) -> None:
        self.user = user
        self.password = password 
        self.host = host 
        self.port = port 
        self.name = name 
        self.db = None
        self.cursor = None
        
        if not ConnectionMySql._pool_initialized:
            ConnectionMySql._initialize_pool(user, password, host, port, name)
    
    @classmethod
    def _initialize_pool(cls, user, password, host, port, name):
        """Initialize the connection pool with retry logic"""
        try:
            cls._connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="mysql_pool",
                pool_size=5,
                host=host,
                user=user,
                password=password,
                database=name,
                port=port,
                autocommit=False,
                pool_reset_session=True,
                connect_timeout=30
            )
            cls._pool_initialized = True
        except Error as e:
            print(f"Error creating connection pool: {e}")
            cls._pool_initialized = False
            raise
    
    def start_con(self):
        """Get a connection with retry logic"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                if self.db is None or not hasattr(self.db, 'is_connected') or not self.db.is_connected():
                    self.db = self._connection_pool.get_connection()
                    self.cursor = self.db.cursor()
                    # Test the connection
                    self.cursor.execute("SELECT 1")
                    self.cursor.fetchone()
                return
            except (Error, InterfaceError, AttributeError) as e:
                if attempt == max_retries - 1:
                    raise
                print(f"Connection attempt {attempt + 1} failed: {str(e)}. Retrying...")
                time.sleep(retry_delay)
                self._cleanup_failed_connection()
    
    def _cleanup_failed_connection(self):
        """Clean up any failed connection state"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.db:
                try:
                    self.db.close()
                except:
                    pass
        except:
            pass
        finally:
            self.cursor = None
            self.db = None
    
    def close_con(self):
        """Safely close connection and return it to the pool"""
        try:
            if self.cursor:
                try:
                    self.cursor.close()
                except:
                    pass
            
            if self.db:
                try:
                    if hasattr(self.db, 'is_connected') and self.db.is_connected():
                        self.db.close()  # This returns it to the pool
                except:
                    pass
        except Exception as e:
            print(f"Error during connection close: {str(e)}")
        finally:
            self.cursor = None
            self.db = None
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.close_con()