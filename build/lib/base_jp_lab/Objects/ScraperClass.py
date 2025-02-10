from selenium.webdriver import Firefox, FirefoxOptions, Chrome, ChromeOptions
from selenium.common.exceptions import NoSuchAttributeException, NoSuchElementException
from selenium.webdriver.common.by import By
from .GetData import scraping_base_url

class InvalidSiteName(Exception):
    pass

class Scraper():
    """ Classe criada para realizar WebScraping """
    def __init__(self, site_name:str, url_add:str, xpath:str, std_wait_time:float = 0):
        """
        Inicializa uma instância da classe 'Scraper'
        
        Args
        ----------
            site_name (str): Nome do site que será acessado.
            url_add (str): Parte que deve ser adicionada à URL para acessar o dado específico que é desejado. Caso haja parte dinâmica dentro dessa string, utilize '{}' e o método 'format()'
        
        Vars
        ----------
            base_url (str): Parte padrão da URL. Se for 'None', não cria o objeto.
            url (str): URL formatada com o resto adicionado em 'url_add'.
            driver_options (Options): Opções extras que podem ser inserídas ao driver.
            driver (Chrome): Objeto que abre o navegador e faz o WebScraping.
            std_wait_time (float): Tempo de espera para completar o objetivo do drive.
            xpath (str): X-Path do elemento que deve ser buscado
        """
        self.base_url = scraping_base_url(site_name)
        if self.base_url is not None:
            self.url = self.base_url.format(url_add)
            self.driver_options = ChromeOptions()
            # self.driver_options.add_argument()
            self.driver = Chrome(self.driver_options)
            self.std_wait_time = std_wait_time
            self.scrapped_data = []
            self.xpath = xpath
        else:
            raise InvalidSiteName('Site inválido para WebScraping')

    def start_scraping(self, search_data:list = []) -> None:
        """
        Inicia a raspagem dos dados
        
        Args
        ----------
            search_data (list): Valores dinâmicos que serão buscados 
        """
        for item in search_data:
            self.driver.get(self.url.format(item))
            self.driver.implicitly_wait(self.std_wait_time)
            self.scrapped_data += self.seach_element(self.xpath)
        self.driver.close()

    def seach_element(self, xpath:str):
        """
        Busca um elemento baseado em um XPATH
        
        Args
        ----------
            xpath (str): Caminho XPATH do elemento desejado
        """
        found_element = self.driver.find_element(By.XPATH, xpath)
        print(found_element.text)
        return found_element.text