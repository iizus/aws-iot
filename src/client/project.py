from src.client.client import Client
import src.client.certs as certs


class Project:
    def __init__(self, name:str='test') -> None:
        self.__name:str = name


    def create_client(self, client_id:str='test') -> Client:
        certs_dir:str = f'{self.__name}/{client_id}'
        
        client:Client = Client(
            project_name = self.__name,
            id = self.__name if client_id == '' else client_id,
            cert = certs.get_cert_path(certs_dir),
            key = certs.get_key_path(certs_dir),
        )
        print(f"[{client.id}] Created client with Cert: {client.cert} and Key: {client.key}")
        return client