from src.client.client import Client
from src.client.certs import Cert


class Project:
    def __init__(self, name:str='test') -> None:
        self.__name:str = name


    def create_client(self, client_id:str='client1') -> Client:
        cert:Cert = Cert(dir=f'{self.__name}/{client_id}')
        client:Client = Client(
            project_name = self.__name,
            id = self.__name if client_id == '' else client_id,
            cert = cert.get_cert_path(),
            key = cert.get_key_path(),
        )
        print(f"[{client.id}] Created client with Cert: {client.cert} and Key: {client.key}")
        return client