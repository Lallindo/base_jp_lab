import httpx
import asyncio
from math import ceil
from typing import Union, List, Optional
from .AccessClass import Access
from .GetData import api_data, api_token_db
from itertools import batched

class AsyncCaller:
    """Classe para realizar chamadas HTTPS de modo assíncrono usando httpx"""
    
    def __init__(self, access: Access = None, site_name: str = '', owner: str = 'silvio'):
        """
        Inicializa uma instância da classe 'AsyncCaller'
        
        Args:
            access (Access): Acesso ao banco de dados
            site_name (str): Nome do site que será acessado
            owner (str, opcional): Nome do dono com todas as letras minúsculas
        """
        api = api_data(access, site_name)

        self.urls = []
        self.std_url = api[1]
        self.headers = eval(api[3])['header']
        self.param = eval(api[5])['params']
        self.chunked_urls = []
        
        if "Authorization" in self.headers and self.headers["Authorization"] == "Bearer {}":
            self.headers['Authorization'] = f"Bearer {api_token_db(access, site_name, owner=owner)}"

    def set_url(self, url: Union[str, List[str]] = None):
        """
        Adiciona urls à lista de urls que serão acessadas
        
        Args:
            url (str|list): Url que deve ser inserida
        """
        if isinstance(url, str):
            self.urls.append(self.std_url.format(url))
        elif isinstance(url, list):
            for i in url:
                self.urls.append(self.std_url.format(i))

    def separate_chunks(self, chunk_size: Union[int, float] = 0):
        """
        Separa o atributo 'urls' em listas menores
        
        Args:
            chunk_size (int|float): Tamanho dos chunks
        """
        if isinstance(chunk_size, float):
            chunk_size = round(chunk_size)

        self.chunked_urls = batched(self.urls, chunk_size)

    async def _fetch_url(self, client: httpx.AsyncClient, url: str, return_full_response: bool):
        """Helper method to fetch a single URL"""
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response if return_full_response else response.json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error for {url}: {e}")
            return None
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    async def make_calls(self, 
                        chunk_size: Union[int, float] = 0, 
                        single_list: bool = True,
                        return_full_response: bool = False) -> Optional[Union[List, List[List]]]:
        """
        Faz as chamadas de modo assíncrono
        
        Args:
            chunk_size (int|float): Tamanho dos chunks
            single_list (bool): Retornar como lista única ou lista de chunks
            return_full_response (bool): Retornar resposta completa ou apenas JSON
            
        Returns:
            List of responses or None if no URLs
        """
        self.chunked_urls = []

        if not self.urls:
            print("Nenhuma URL adicionada")
            return None

        async with httpx.AsyncClient(headers=self.headers) as client:
            if chunk_size == 0:
                tasks = [self._fetch_url(client, url, return_full_response) for url in self.urls]
                return await asyncio.gather(*tasks)
            else:
                if chunk_size > 0 and not self.chunked_urls:
                    self.separate_chunks(chunk_size)

                results = []
                for chunk in self.chunked_urls:
                    print(f"Request em chunk com tamanho {len(chunk)}")
                    tasks = [self._fetch_url(client, url, return_full_response) for url in chunk]
                    chunk_result = await asyncio.gather(*tasks)
                    
                    if single_list:
                        results.extend(chunk_result)
                    else:
                        results.append(chunk_result)
                
                return results