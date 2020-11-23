import os
import csv
import re
from zipfile import ZipFile
import requests
from dotenv import load_dotenv
from tqdm import tqdm


def _load_env_vars(path=None):
    load_dotenv(path)
    env_vars = {
        'NAME': os.getenv('NAME'),
        'URL': os.getenv('URL'),
        'EXPECTED_FORMAT': os.getenv('EXPECTED_FORMAT'),
        'UG_PRIMARIA': os.getenv('UG_PRIMARIA'),
        'UG_SECUNDARIA': os.getenv('UG_SECUNDARIA'),
        'DAY': os.getenv('DAY'),
        'MONTH': os.getenv('MONTH'),
        'YEAR': os.getenv('YEAR')
    }
    return env_vars


def _prompt_user(values=None):
    values = {
        'day': input('Digite o dia: '),
        'month': input('Digite o mês: '),
        'year': input('Digite o ano: ')
    }
    return values


def _download_file(url, date):
    response = requests.get(
        url+date,
        verify=False,
        stream=True
    )
    total_size_in_bytes = int(response.headers.get('content-length', 0))
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


def _parse_empenho(date):
    file_name = date + '_Despesas_Empenho'
    ug = (
        env_vars['UG_PRIMARIA'],
        env_vars['UG_SECUNDARIA']
    )
    output = open(date + '_Output.csv', 'w', encoding='latin-1')
    with open(file_name + '.csv', encoding='latin-1') as f:
        reader = csv.reader(f, delimiter=';')
        writer = csv.writer(output)
        for line in reader:
            if line[12] in ug:
                writer.writerow((
                    line[12],
                    line[2],
                    line[3],
                    line[6],
                    line[7],
                    line[18],
                    _filter('CODOM([0-9]+)', '[0-9]+', line[18]),
                    _filter('RQ([0-9]+)', '[0-9]+', line[18]),
                    _filter('NC([0-9]+)', '[0-9]+', line[18]),
                    _filter('SRP([0-9]+/[0-9]{4}-[0-9]{6})',
                            '[0-9]+/[0-9]{4}-[0-9]{6}', line[18]),
                    _filter('OBS([\\w]+)', '\\w', line[18]),
                    line[45]+line[47]+line[49]+line[51],
                    line[60]
                ))


def _filter(shell, kernel, string):
    result = re.search(shell, string)
    if result:
        return re.search(kernel, result)
    else:
        return None


env_vars = _load_env_vars()
user_input = _prompt_user()
date = user_input['year'] + user_input['month'] + user_input['day']
_download_file(env_vars['URL'], date)
file_name = 'despesa' + date + env_vars['EXPECTED_FORMAT']
if env_vars['EXPECTED_FORMAT'] == '.zip':
    _unzip_file(file_name)
_parse_empenho(date)
print('Success!')
