from typing import Tuple
from glob import glob



defaul_cert_dir:str = 'test/client1'
    
def get_ca_path(type:str='RSA2048') -> str:
    '''
    >>> get_ca_path()
    'certs/ca/RSA2048/AmazonRootCA1.pem'
    '''
    ca_path:str = __get_file_path_of(project_path=f'ca/{type}', file_type='pem')
    return ca_path


def get_certs_path(certs_dir:str=defaul_cert_dir) -> Tuple[str]:
    '''
    >>> get_certs_path()
    ('certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-certificate.pem.crt', 'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-private.pem.key')
    '''
    cert_path:str = get_cert_path(certs_dir)
    key_path:str = get_key_path(certs_dir)
    return cert_path, key_path


def get_cert_path(certs_dir:str=defaul_cert_dir) -> str:
    '''
    >>> get_cert_path()
    'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-certificate.pem.crt'
    '''
    cert_path:str = __get_certs_path_of(certs_dir, cert_type='crt')
    return cert_path


def get_key_path(certs_dir:str=defaul_cert_dir) -> str:
    '''
    >>> get_key_path()
    'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-private.pem.key'
    '''
    key_path:str = __get_certs_path_of(certs_dir, cert_type='key')
    return key_path


def __get_certs_path_of(certs_dir:str, cert_type:str) -> str:
    '''
    >>> __get_certs_path_of(certs_dir='test/client1', cert_type='crt')
    'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-certificate.pem.crt'
    >>> __get_certs_path_of(certs_dir='test/client1', cert_type='key')
    'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-private.pem.key'
    '''
    cert_path:str = __get_file_path_of(
        project_path = certs_dir,
        file_type = cert_type
    )
    return cert_path


def __get_file_path_of(project_path:str, file_type:str) -> str:
    '''
    >>> __get_file_path_of(project_path='ca/RSA2048', file_type='pem')
    'certs/ca/RSA2048/AmazonRootCA1.pem'
    '''
    files_path:str = f"certs/{project_path}/*.{file_type}"
    file_path:str = glob(files_path)[0]
    return file_path



class Cert:
    def __init__(self, dir:str=defaul_cert_dir) -> None:
        self.__dir:str = dir


    def get_ca_path(self, type:str='RSA2048') -> str:
        '''
        >>> cert:Cert = Cert('test/client1')
        >>> cert.get_ca_path()
        'certs/ca/RSA2048/AmazonRootCA1.pem'
        '''
        ca_path:str = get_ca_path(type)
        return ca_path


    def get_certs_path(self) -> Tuple[str]:
        '''
        >>> cert:Cert = Cert('test/client1')
        >>> cert.get_certs_path()
        ('certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-certificate.pem.crt', 'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-private.pem.key')
        '''
        cert_path:str = self.get_cert_path()
        key_path:str = self.get_key_path()
        return cert_path, key_path


    def get_cert_path(self) -> str:
        '''
        >>> cert:Cert = Cert('test/client1')
        >>> cert.get_cert_path()
        'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-certificate.pem.crt'
        '''
        cert_path:str = get_cert_path(self.__dir)
        return cert_path


    def get_key_path(self) -> str:
        '''
        >>> cert:Cert = Cert('test/client1')
        >>> cert.get_key_path()
        'certs/test/client1/445e94124ab35ff287cbbb0cfbd0d2dc62e846647a8ccb5734e99de88a1f14d7-private.pem.key'
        '''
        key_path:str = get_key_path(self.__dir)
        return key_path



if __name__ == '__main__':
    from doctest import testmod
    testmod()