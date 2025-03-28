from .ConnectionMySqlClass import ConnectionMySql
from .ConnectionPGClass import ConnectionPG

class Access():
    """ Classe criada para acessar o banco de dados de modo centralizado """
    
    def __init__(self, user:str, password:str, host:str, port:str, name:str, is_mysql:bool = True):
        """
        Inicializa uma instância da classe 'Access' instânciando um objeto 'Connection'
        
        Args
        ----------
            user (str): Nome do usuário para a conexão com o banco de dados.
            password (str): Senha usada para a conexão com o banco de dados. 
            host (str): Host do banco de dados, pode ser alterado para 'localhost' para acessar um banco local. 
            port (str): Porta usada para a conexão com o banco.
            name (str): Nome do banco de dados. 

        Vars
        ----------
            con (Connection): Conexão estabelecida com o banco de dados.

        Notas
        ----------
            Todos os métodos devem iniciar com o método "self.con.start_con()" e terminar com o método "self.con.close_con()"
        """
        self.is_mysql = is_mysql
        if is_mysql:
            self.con = ConnectionMySql(user, password, host, port, name)
        else:
            self.con = ConnectionPG(user, password, host, port, name)
        
    def get_api_data(self, id_api:int) -> list:
        """
        Busca os dados necessários para a API no banco de dados
        
        Args
        ----------
            id_api (int): Id da respectiva API no banco de dados
        """
        return self.custom_select_query(f"SELECT * FROM apis WHERE id_api = {id_api}")
        
    def custom_select_query(self, query:str) -> list|dict:
        """
        Processa uma query inteiramente feita pelo usuário
        
        Args
        ----------
            query (str): Query feita pelo usuário.
        """
        self.con.start_con()
        self.con.cursor.execute(query)
        return_val = self.con.cursor.fetchall()
        self.con.close_con()
        return return_val
    
    def custom_i_u_query(self, query:str, data:list) -> None:
        """
        Insere ou altera dados no banco baseado na query e nos dados enviados pelo usuário
        
        Args
        ----------
            query (str): Query feita pelo usuário.
            data (list): Lista com os dados que serão inseridos
        """
        self.con.start_con()
        self.con.cursor.executemany(query, data)
        self.con.db.commit()
        #if self.is_mysql:
        #    self.con.cursor.executemany(query, data)
        #    self.con.db.commit()
        #else:
        #    args = ','.join(self.con.cursor.mogrify("(%s, %s, %s)", i).decode('utf-8') for i in data)
        #    self.con.cursor.execute(query + args)
        #    self.con.db.commit()
        self.con.close_con()
        print('Dados inseridos/alterados')
        return 