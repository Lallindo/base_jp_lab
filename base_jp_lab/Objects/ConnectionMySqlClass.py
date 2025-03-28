import mysql.connector

class ConnectionMySql():
    """ Classe criada para controlar a conexão com o banco de dados """
    
    def __init__(self, user:str, password:str, host:str, port:str, name:str) -> None:
        """
        Inicializa uma instância da classe 'Connection'
        
        Args
        ----------
            user (str): Nome do usuário para a conexão com o banco de dados.
            password (str): Senha usada para a conexão com o banco de dados. 
            host (str): Host do banco de dados, pode ser alterado para 'localhost' para acessar um banco local. 
            port (str): Porta usada para a conexão com o banco.
            name (str): Nome do banco de dados. 

        Vars
        ----------
            db (mysql.connector.connection.MySQLConnection): Conexão com o banco através de 'mysql.connector.connect()'.
            cursor (mysql.connector.cursor.MySQLCursor): Cursor usado para realizar as queries.
        """
        self.user = user
        self.password = password 
        self.host = host 
        self.port = port 
        self.name = name 
        self.db = None
        self.cursor = None
        
    def start_con(self):
        """
        Inicializa a conexão com o banco e liga as variáveis 'self.db' e 'self.cursor' 
        com, respectivamente, o 'mysql.connector.connect()' e o 'mysql.connector.cursor.MySQLCursor'
        """
        self.db = mysql.connector.connect(
            host=self.host, 
            user = self.user,
            password=self.password,
            database=self.name,
            port=self.port)
        self.cursor = self.db.cursor()
        
    def close_con(self):
        """
        Fecha a conexão com o banco
        """
        self.cursor.close()
        self.db.close()
        
    
    