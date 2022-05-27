from typing import List
from glob import glob

    
def get_ca_path() -> str:
    # '''
    # >>> get_ca_path()
    # 'certs/ca/RSA1/AmazonRootCA1.pem'
    # '''
    ca_path = __get_file_path_of(project_path='ca', file_type='pem')
    return ca_path


def get_certs_path_of(project_name:str) -> List[str]:
    # '''
    # >>> get_certs_path_of(project_name='test')
    # ('certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt', 'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key')
    # '''
    cert_path = get_cert_path_of(project_name='test')
    key_path = get_key_path_of(project_name='test')
    return cert_path, key_path


def get_cert_path_of(project_name:str) -> str:
    # '''
    # >>> get_cert_path_of(project_name='test')
    # 'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt'
    # '''
    cert_path = __get_certs_path_of(project_name, cert_type='crt')
    return cert_path


def get_key_path_of(project_name:str) -> str:
    # '''
    # >>> get_key_path_of(project_name='test')
    # 'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key'
    # '''
    cert_path = __get_certs_path_of(project_name, cert_type='key')
    return cert_path


def __get_certs_path_of(project_name:str, cert_type:str) -> str:
    # '''
    # >>> __get_certs_path_of(project_name='test', cert_type='crt')
    # 'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt'
    # >>> __get_certs_path_of(project_name='test', cert_type='key')
    # 'certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key'
    # '''
    cert_path = __get_file_path_of(
        project_path = project_name,
        file_type = cert_type
    )
    return cert_path


def __get_file_path_of(project_path:str, file_type:str) -> str:
    '''
    >>> __get_file_path_of(project_path='ca/RSA2048', file_type='pem')
    'certs/ca/RSA2048/AmazonRootCA1.pem'
    '''
    files_path = f"certs/{project_path}/*.{file_type}"
    # print(files_path)
    # print(glob(files_path))
    file_path = glob(files_path)[0]
    return file_path


if __name__ == '__main__':
    from doctest import testmod
    testmod()