import psycopg2

class ConnectionPG:
    """ Classe criada para controlar a conexão com o banco de dados Postgree """

    def __init__(self, user:str = '', password:str = '', host:str = '', port:str = '', name:str = '') -> None:
        """
        Inicializa uma instância da classe 'ConnectionPG'
        
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
        self.database = name
        self.db = None
        self.cursor = None

    def start_con(self):
        self.db = psycopg2.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )
        self.cursor = self.db.cursor()

    def close_con(self):
        self.cursor.close()
        self.db.close()