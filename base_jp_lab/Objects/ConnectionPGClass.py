import psycopg2
from psycopg2 import pool
from typing import Optional

class ConnectionPG:
    """Classe para controlar a conexão com PostgreSQL com connection pooling"""
    
    _connection_pool = None
    
    def __init__(self, user: str = '', password: str = '', host: str = '', port: str = '', name: str = ''):
        """
        Inicializa a classe com configurações de conexão
        
        Args:
            user (str): Nome do usuário
            password (str): Senha do banco
            host (str): Host do banco
            port (str): Porta do banco
            name (str): Nome do banco
        """
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = name
        self.db = None
        self.cursor = None
        
        # Initialize connection pool if not already done
        if ConnectionPG._connection_pool is None:
            ConnectionPG._initialize_pool(user, password, host, port, name)
    
    @classmethod
    def _initialize_pool(cls, user, password, host, port, name):
        """Initialize the connection pool"""
        try:
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=5,
                user=user,
                password=password,
                host=host,
                port=port,
                database=name
            )
        except Exception as e:
            print(f"Error creating connection pool: {e}")
            raise
    
    def start_con(self):
        """Obtém uma conexão do pool"""
        try:
            if self.db is None or self.db.closed:
                self.db = self._connection_pool.getconn()
                self.cursor = self.db.cursor()
        except Exception as e:
            print(f"Error getting connection from pool: {e}")
            raise
    
    def close_con(self):
        """Fecha a conexão e retorna ao pool"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.db and not self.db.closed:
                self._connection_pool.putconn(self.db)
            # Reset references
            self.cursor = None
            self.db = None
        except Exception as e:
            print(f"Error closing connection: {e}")