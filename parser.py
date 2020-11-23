import os
from zipfile import ZipFile
import requests
from dotenv import load_dotenv
from tqdm import tqdm


def _load_env_vars(path=None):
    load_dotenv(path)
    env_vars = {
        'NAME': os.getenv('NAME'),
        'URL': os.getenv('URL'),
        'EXPECTED_FORMAT': os.getenv('EXPECTED_FORMAT')
    }
    return env_vars

def _prompt_user(values=None):
    values = {
        'day': input('Digite o dia: '),
        'month': input('Digite o mês: '),
        'year': input('Digite o ano: '),
        'ug': input('Digite a Unidade Gestora: ')
    }
    return values

def _download_file(url, date):   
    response = requests.get(
        url+date, 
        verify=False,
        stream=True
        )
    total_size_in_bytes= int(response.headers.get('content-length', 0))
    block_size = 1024
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    file_name = 'despesa' + date + env_vars['EXPECTED_FORMAT']

    with open(file_name, 'wb') as f:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            f.write(data)
        progress_bar.close()

def _unzip_file(file_name):
    with ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall()


env_vars = _load_env_vars()
user_input = _prompt_user()
date = user_input['year'] + user_input['month'] + user_input['day']
_download_file(env_vars['URL'], date)
file_name = 'despesa' + date + env_vars['EXPECTED_FORMAT']
if env_vars['EXPECTED_FORMAT'] == '.zip':
    _unzip_file(file_name)
print('Success!')