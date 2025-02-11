import requests
from .AccessClass import Access 
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from cryptography.fernet import Fernet

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

def encrypt_msg(message:str, key:str):
    """
    Encripta uma string usando Fernet.
    
    Args
    ----------
        message (str): String que será criptografada.
        key (str): Chave de criptografia que será usada. 
    """
    fernet = Fernet(key)
    return fernet.encrypt(message.encode()).decode()

def decrypt_msg(message:str, site_name:str, keys_json_path:str = 'base_jp_lab/Configs/decrypt_keys.json', override_key:str = ''):
    """
    Decripta uma string usando Fernet.
    
    Args
    ----------
        message (str): String que será criptografada.
        site_name (str): Nome do site de onde o valor criptografado vem. 
        keys_json_path (str): Caminho até o arquivo JSON com as chaves de criptografia.
        override_key (str): Utiliza uma nova chave e ignora a chave no arquivo JSON.
    """
    if override_key == '':
        with open(keys_json_path, 'r') as f:
            key = json.load(f)['keys'][f'{site_name}_key']
    else:
        key = override_key

    fernet = Fernet(key)
    return fernet.decrypt(message).decode()

def set_api_keys(keys_json_path:str = 'base_jp_lab/Configs/decrypt_keys.json') -> None:
    """
    Configura as chaves de API e as adiciona, criptografadas, ao banco. 
    
    Args
    ----------
        keys_json_path (str): Caminho para o arquivo JSON com as chaves de criptografia.
    """
    key = Fernet.generate_key()
    loja_id = input('Qual o site que você deseja cadastrar?\n0 - Tiny\n1 - PedidoOK\n2 - Mercado Livre\n3 - Magalu\n4 - Amazon\n5 - Shopee')
    match loja_id:
        case '0':
            nome_loja = 'tiny'
        case '1':
            nome_loja = 'pedidook'
        case '2':
            nome_loja = 'mercadolivre'
        case '3':
            nome_loja = 'magalu'
        case '4':
            nome_loja = 'amazon'
        case '5':
            nome_loja = 'shopee' 
        case default:
            print('Número digitado não é válido!')
    client_id = input('Digite seu client_id:')
    client_secret = input('Digite seu client_secret:')
    refresh_token = input('Digite seu refresh_token:')

    enc_client_id = encrypt_msg(client_id, key)
    enc_client_secret = encrypt_msg(client_secret, key)
    enc_refresh_token = encrypt_msg(refresh_token, key)

    with open(keys_json_path, 'r') as f:
        keys = dict(json.load(f))

    keys['keys'][f'{nome_loja}_key'] = key.decode()

    with open(keys_json_path, 'w') as f:
        json.dump(keys, f, indent=1)

    a = Access('root', '', 'localhost', '3306', 'jp_bd')
    data = [(enc_client_id, enc_client_secret, enc_refresh_token, int(loja_id) + 1)]
    a.custom_i_u_query('UPDATE apis SET client_id_api = %s, client_secret_api = %s, refresh_token_api = %s WHERE id_api = %s', data)