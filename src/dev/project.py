from client import Client
import certs


class Project:
    def __init__(self, name:str='test') -> None:
        self.__name:str = name


    def create_client_using(self, certs_dir:str='', proxy=None) -> Client:
        certs_path:str = f'{self.__name}/{certs_dir}'
        
        client:Client = Client(
            id = self.__name if certs_dir == '' else certs_dir,
            cert = certs.get_cert_path(certs_path),
            key = certs.get_key_path(certs_path),
            proxy = proxy,
        )
        print(f"""Creating client with 
            Client ID: {client.id}
            Cert: {client.cert}
            Key: {client.key}""")
        return client