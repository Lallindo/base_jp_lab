from .ConnectionMySqlClass import ConnectionMySql
from .ConnectionPGClass import ConnectionPG
from typing import Union, List, Dict, Any
import time

class Access():
    """Enhanced database access class with better error handling"""
    
    def __init__(self, user: str, password: str, host: str, port: str, name: str, is_mysql: bool = True):
        self.is_mysql = is_mysql
        if is_mysql:
            self.con = ConnectionMySql(user, password, host, port, name)
        else:
            self.con = ConnectionPG(user, password, host, port, name)
        
    def get_api_data(self, id_api: int) -> List[Dict[str, Any]]:
        """Safe query with retry logic"""
        return self._execute_with_retry(
            "SELECT * FROM apis WHERE id_api = %s", 
            (id_api,),
            is_select=True
        )
        
    def custom_select_query(self, query: str, params: tuple = None) -> Union[List[Dict[str, Any]], List[tuple]]:
        """Safe select query with retry logic"""
        return self._execute_with_retry(query, params, is_select=True)
    
    def custom_i_u_query(self, query: str, data: Union[List[tuple], tuple]) -> None:
        """Safe insert/update query with retry logic"""
        self._execute_with_retry(query, data, is_select=False)
    
    def _execute_with_retry(self, query: str, params: Any = None, is_select: bool = True) -> Any:
        """Core method with retry logic for all queries"""
        max_retries = 3
        retry_delay = 1  # seconds
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                self.con.start_con()
                
                if isinstance(params, list):
                    self.con.cursor.executemany(query, params)
                elif params:
                    self.con.cursor.execute(query, params)
                else:
                    self.con.cursor.execute(query)
                
                if not is_select:
                    self.con.db.commit()
                    print('Dados inseridos/alterados com sucesso')
                    return None
                
                result = self.con.cursor.fetchall()
                return result
                
            except Exception as e:
                last_exception = e
                print(f"Database error (attempt {attempt + 1}): {str(e)}")
                
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    self.con.close_con()  # Ensure clean state for retry
                else:
                    # On final attempt, try to rollback if it was a write operation
                    if not is_select and hasattr(self.con, 'db') and self.con.db:
                        try:
                            self.con.db.rollback()
                        except:
                            pass
                    raise
            finally:
                try:
                    self.con.close_con()
                except Exception as e:
                    print(f"Error closing connection: {str(e)}")
        
        raise last_exception if last_exception else Exception("Unknown database error")