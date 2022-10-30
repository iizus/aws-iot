from src.client.certs import Cert
from src.client.client import Client


class Project:
    def __init__(self, name:str='test') -> None:
        self.__name:str = name

    def create_client(self, client_id:str='client1', cert_dir:str='') -> Client:
        cert_dir:str = f'{self.__name}/{cert_dir}{client_id}'
        return Client(
            project_name = self.__name,
            id = self.__name if client_id == '' else client_id,
            cert = Cert(cert_dir)
        )