import requests
import json
from requests.exceptions import HTTPError, JSONDecodeError
from requests.adapters import HTTPAdapter, Retry
from .AccessClass import Access
from .GetData import api_token_n8n, api_data

class Caller():
    """ Classe criada para realizar chamadas HTTPS e gerenciar os dados necessários para essas chamadas """
    def __init__(self, access:Access, site_name:str, link_n8n:str, owner:str = ''):
        """
        Inicializa uma instância da classe 'Caller'
        
        Args
        ----------
            access (Access): Acesso ao banco de dados.
            site_name (str): Nome do site que será acessado.
            link_n8n (str): URL do webhook do N8N
            owner (str, opcional): Nome do dono com todas as letras minúsculas.
        
        Vars
        ----------
            std_url (str): URL do endpoint da API sem formatação. String apenas aponta para a url e deve ser alterada para acessar dados específicos.
            header (dict): Valores padrões do header.
            param (dict): Valores padrões dos parâmetros.
            token_name (str): Nome do valor em que a chave da API é retornado.
            session (requests.Session): Objeto Session usado para manter informações entre diferentes requests.
            
        Extra
        ----------
            retry_strategy (requests.adapters.Retry): Cria a "estratégia" de quando e quantas vezes refazer um request que falhou.
            
        Notas
        ----------
            A inserção em 'std_url', 'header', 'param' e 'token_name' foram feitos baseados na estrutura do banco de dados `jp_bd.apis`.
        """
        
        api = api_data(access, site_name)
        self.std_url = api[1]
        self.req_url = ''
        self.header = eval(api[3])['header']
        self.param = eval(api[5])['params']
        self.token_name = api[7]
        
        self.session = requests.Session()
        self.session.headers = self.header
        self.session.params = self.param
        
        if 'Authorization' in self.session.headers and self.session.headers['Authorization'] == 'Bearer {}':
            print('Pegando chave de API:')
            self.session.headers.update({'Authorization': f'Bearer {api_token_n8n(link_n8n, site_name, owner)[self.token_name]}'})
            
        retry_strategy = Retry(
            total=5, # Quantidade de tentativas máximas
            backoff_factor=0.2, # Tempo entre será (backoff_factor) * (2 ** (tentativas_falhadas - 1)) -> Com 0.1 = 0.1, 0.2, 0.4, 0.8, 1.6
            allowed_methods=['GET', 'POST', 'PUT', 'PATCH', 'OPTIONS'],
            status_forcelist=[429, 500, 502, 503, 504], # Resultados que serão repetidos
            raise_on_status=True)
        self.session.mount('https://', HTTPAdapter(max_retries=retry_strategy))
        self.session.mount('http://', HTTPAdapter(max_retries=retry_strategy))
    
    def print_all(self):
        print(f'URL: {self.std_url}')
        print(f'Headers: {self.header}')
        print(f'Parâmetros: {self.param}')
    
    def make_call(self, add_to_url:str = '', method:str = 'get', params_add:dict = {}, data_post:dict = {}, disable_std_params:bool = False) -> dict:
        """
        Realiza uma chamada com base nos args inseridos
        
        Args:
            add_to_url (str): Valor que deve ser adicionado ao fim da url da api para especificar os dados que serão buscados.
            method (str): Método utilizado pela chamada ('GET', 'POST', 'PUT', etc).
            params_add (dict): Parâmetros adicionais que devem ser adicionados à chamada.
            data_post (dict): Dados que serão enviados num POST ou PUT.
            disable_std_params (bool): Desabilita os parâmetros padrões.
        """
        
        if disable_std_params: self.session.params = {}
        if params_add != {}: self.session.params.update(params_add)
        
        self.req_url = self.std_url.format(add_to_url) if add_to_url != '' else self.std_url[:-2]
        try:
            call = self.session.request(
                method = method,
                url = self.req_url,
                data = None if method.lower() not in ['post', 'put'] else json.dumps(data_post)
            )
            call.raise_for_status()
        except HTTPError as er1:
            print(f'Erro HTTP. Código {er1.response.status_code}')
        
        print(f'Chamada feita. Resposta com código {call.status_code}')
        
        return call.json()