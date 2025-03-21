import grequests
from math import ceil
from .AccessClass import Access
from .GetData import api_data, api_token_db

class AsyncCaller:
    """ Classe criada para realizar chamadas HTTPS de modo assíncrono """
    def __init__(self, access:Access = None, site_name:str = '', owner:str = 'silvio'):
        """
        Inicializa uma instância da classe 'AsyncCaller'
        
        Args
        ----------
            access (Access): Acesso ao banco de dados.
            site_name (str): Nome do site que será acessado.
            owner (str, opcional): Nome do dono com todas as letras minúsculas.
        
        Vars
        ----------
            urls (list): Lista com os endpoints que serão buscados.
            std_url (str): URL do endpoint da API sem formatação. String apenas aponta para a url e deve ser alterada para acessar dados específicos.
            header (dict): Valores padrões do header.
            param (dict): Valores padrões dos parâmetros.
            chunked_urls (list): Lista com os endpoints separados para limitar a quantidade de requests feitos simultâneamentes.
            
        Notas
        ----------
            A inserção em 'std_url', 'header' e 'params' foram feitos baseados na estrutura do banco de dados `jp_bd.apis`.
        """

        api = api_data(access, site_name)

        self.urls = []
        self.std_url = api[1]
        self.headers = eval(api[3])['header']
        self.param = eval(api[5])['params']
        self.chunked_urls = []
        if "Authorization" in self.headers and self.headers["Authorization"] == "Bearer {}":
            self.headers['Authorization'] = f"Bearer {api_token_db(access, site_name, owner=owner)}"
        else:
            pass 

    def set_url(self, url:str|list = None):
        """
        Adiciona urls à lista de urls que serão acessadas
        
        Args
        ----------
            url (str|list): Url que deve ser inserida.    

        Notas
        ----------
            Se a URL for uma (str) ela é adicionada à lista com 'append', 
            caso seja uma (list) ela é passada por um 'for loop' e os valores são adicionadas com 'append'. 

        """
        if type(url) == str:
            self.urls.append(self.std_url.format(url))
        elif type(url) == list:
            for i in url:
                self.urls.append(self.std_url.format(i))

    def separate_chunks(self, chunk_size:int|float = 0):
        """
        Separa o atríbuto 'urls' em listas menores
        
        Args
        ----------
            chunk_size (int|float): Tamanho dos 'pedaços' em que as urls serão separadas. 
            Se for float, o valor é arredondado para o número inteiro mais próximo.

        """
        if type(chunk_size) == float:
            chunk_size = round(chunk_size)

        for i in range(ceil(len(self.urls) / chunk_size)):
            self.chunked_urls.append(
                self.urls
                [
                    len(self.chunked_urls)*chunk_size:
                    (len(self.chunked_urls)+1)*chunk_size]
                )

    def make_calls(self, chunk_size:int|float = 0, single_list:bool = True,return_full_response:bool = False):
        """
        Faz as chamadas de modo assíncrono
        
        Args
        ----------
            chunk_size (int|float): Tamanho dos 'pedaços' em que as urls serão separadas. 
            single_list (bool): Define se os dados devem ser retornados em uma lista ou separo em listas idênticas aos chunks definidos.
            return_full_respose (bool): Define se o retorno será uma 'AsyncResponse' ou um 'dict' formado com o json da resposta.

        """
        if len(self.urls) == 0:
            print("Nenhuma URL adicionada")
            return None

        if chunk_size == 0:
            get_list = [grequests.get(i, headers=self.headers) for i in self.urls]
            if not return_full_response:
                requests = [i.json() for i in grequests.map(get_list)]
            else:
                requests = grequests.map(get_list)
            return requests
        elif chunk_size > 0:
            self.separate_chunks(chunk_size)

            chunked_request = []

            for i in self.chunked_urls:
                get_list = [grequests.get(j, headers=self.headers) for j in i]
                print(f"Request em chunck com tamanho {len(i)}")
                if not return_full_response:
                    if single_list:
                        chunked_request += [j.json() for j in grequests.map(get_list)]
                    else:
                        chunked_request.append([j.json() for j in grequests.map(get_list)])
                else:
                    if single_list:
                        chunked_request += [j.json() for j in grequests.map(get_list)]
                    else:
                        chunked_request.append([j.json() for j in grequests.map(get_list)])
            return chunked_request