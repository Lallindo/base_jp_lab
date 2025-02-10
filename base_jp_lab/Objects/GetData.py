import requests
from .AccessClass import Access 
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def api_token_n8n(link_n8n:str, site_name:str, owner:str = '',) -> dict:
    """
    Busca a chave de API no flow do N8N
    
    Args
    ----------
        site_name (str): Nome do site que será acessado.
        link_n8n (str): URL do webhook do N8N
        owner (str, opcional): Nome do dono com todas as letras minúsculas.
    """
    r = requests.get(
        url=link_n8n,
        headers={'type':site_name, 'owner':owner}
    )
    return r.json()

def api_data(access:Access, site_name:str) -> tuple:
    """
    Faz o "middle-man" entre a classe 'Caller' e a 'Access'
    
    Args
    ----------
        access (Access): Acesso ao banco.
        site_name (str): Nome do site que será acessado.
    """
    match site_name:
        case 'tiny':
            return access.get_api_data(1)[0]
        case 'pedidook':
            return access.get_api_data(2)[0]
        case 'mercadolivre':
            return access.get_api_data(3)[0]
        case 'magalu':
            return access.get_api_data(4)[0]
        case 'shopee':
            return None
        case 'amazon':
            return None
        
def scraping_base_url(site_name:str) -> str|None:
    """
    Busca a url do marketplace que será usado  
    
    Args
    ----------
        site_name (str): Nome do site que será acessado.
    """
    if site_name in ['pedidook', 'tiny', 'mercadolivre', 'amazon']:
        return None
    elif site_name == 'magalu':
        return 'https://magazineluiza.com.br/{}'
    
def sheet_data(sheet_name:str, creds_location:str, worksheet_id:int = None):
    """
    Busca dados do sheets
    
    Args
    ----------
        sheet_name (str): Nome da planilha que será acessada.
        creds_location (str): Caminho até o arquivo json que contém as credenciais para fazer a conexão ao Sheets.
        worksheet_id (int): GID de uma página dentro da planilha. O GID pode ser encontrado no final da URL ao acessar a página. 
    """
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_location, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).sheet1 if worksheet_id is None else client.open(sheet_name).get_worksheet_by_id(worksheet_id) 
    return sheet.get_all_records()

def alter_sheet(sheet_name:str, creds_location:str, data:list, worksheet_id:int = None):
    """
    Altera ou adiciona dados à uma planilha
    
    Args
    ----------
        sheet_name (str): Nome da planilha que será acessada.
        creds_location (str): Caminho até o arquivo json que contém as credenciais para fazer a conexão ao Sheets.
        data (list): Dados que devem ser inseridos na planilha.
        worksheet_id (int): GID de uma página dentro da planilha. O GID pode ser encontrado no final da URL ao acessar a página. 
    """
    pass