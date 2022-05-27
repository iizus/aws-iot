from client import Client
import certs


class Project:
    def __init__(self, endpoint:str, name:str='test') -> None:
        self.__endpoint:str = endpoint
        self.__name:str = name


    def create_client_using(self, certs_dir:str='') -> Client:
        client:Client = Client(
            endpoint = self.__endpoint,
            client_id = self.__name if certs_dir is None else certs_dir,
            certs_path = f'{self.__name}/{certs_dir}',
        )
        return client