from typing import List
from glob import glob

    
def get_ca_path() -> str:
    '''
    >>> get_ca_path()
    'certs/AmazonRootCA1.pem'
    '''
    ca_path = __get_file_path_of(project_path='', file_type='pem')
    return ca_path


def get_certs_path_of(project_name:str) -> List[str]:
    '''
    >>> get_certs_path_of(project_name='test')
    ('certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt', 'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key')
    '''
    cert_path = __get_cert_path_of(project_name='test')
    key_path = __get_key_path_of(project_name='test')
    return cert_path, key_path


def __get_cert_path_of(project_name:str) -> str:
    '''
    >>> __get_cert_path_of(project_name='test')
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt'
    '''
    cert_path = __get_certs_path_of(project_name, cert_type='crt')
    return cert_path


def __get_key_path_of(project_name:str) -> str:
    '''
    >>> __get_key_path_of(project_name='test')
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key'
    '''
    cert_path = __get_certs_path_of(project_name, cert_type='key')
    return cert_path


def __get_certs_path_of(project_name:str, cert_type:str) -> str:
    '''
    >>> __get_certs_path_of(project_name='test', cert_type='crt')
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt'
    >>> __get_certs_path_of(project_name='test', cert_type='key')
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key'
    '''
    cert_path = __get_file_path_of(
        project_path = f'{project_name}/',
        file_type = cert_type
    )
    return cert_path


def __get_file_path_of(project_path:str, file_type:str) -> str:
    '''
    >>> __get_file_path_of(project_path='', file_type='pem')
    'certs/AmazonRootCA1.pem'
    '''
    files_path = f"certs/{project_path}*.{file_type}"
    filr_path = glob(files_path)[0]
    return filr_path


if __name__ == '__main__':
    from doctest import testmod
    testmod()