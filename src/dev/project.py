from client import Client
import certs


class Project:
    def __init__(self, name:str='test') -> None:
        self.__name:str = name


    def create_client_using(self, client_id:str='') -> Client:
        certs_dir:str = f'{self.__name}/{client_id}'
        
        client:Client = Client(
            project_name = self.__name,
            id = self.__name if client_id == '' else client_id,
            cert = certs.get_cert_path(certs_dir),
            key = certs.get_key_path(certs_dir),
        )
        print(f"""Creating client with 
            Client ID: {client.id}
            Cert: {client.cert}
            Key: {client.key}""")
        return client