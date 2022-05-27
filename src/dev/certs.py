from typing import List
from glob import glob

    
def get_ca_path(type:str='RSA2048') -> str:
    '''
    >>> get_ca_path()
    'certs/ca/RSA2048/AmazonRootCA1.pem'
    '''
    ca_path = __get_file_path_of(project_path=f'ca/{type}', file_type='pem')
    return ca_path


def get_certs_path(certs_dir:str='test') -> List[str]:
    '''
    >>> get_certs_path()
    ('certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt', 'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key')
    '''
    cert_path = get_cert_path(certs_dir)
    key_path = get_key_path(certs_dir)
    return cert_path, key_path


def get_cert_path(certs_dir:str='test') -> str:
    '''
    >>> get_cert_path()
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt'
    '''
    cert_path = __get_certs_path_of(certs_dir, cert_type='crt')
    return cert_path


def get_key_path(certs_dir:str='test') -> str:
    '''
    >>> get_key_path()
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key'
    '''
    cert_path = __get_certs_path_of(certs_dir, cert_type='key')
    return cert_path


def __get_certs_path_of(certs_dir:str, cert_type:str) -> str:
    '''
    >>> __get_certs_path_of(certs_dir='test', cert_type='crt')
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt'
    >>> __get_certs_path_of(certs_dir='test', cert_type='key')
    'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key'
    '''
    cert_path = __get_file_path_of(
        project_path = certs_dir,
        file_type = cert_type
    )
    return cert_path


def __get_file_path_of(project_path:str, file_type:str) -> str:
    '''
    >>> __get_file_path_of(project_path='ca/RSA2048', file_type='pem')
    'certs/ca/RSA2048/AmazonRootCA1.pem'
    '''
    files_path = f"certs/{project_path}/*.{file_type}"
    file_path = glob(files_path)[0]
    return file_path


if __name__ == '__main__':
    from doctest import testmod
    testmod()