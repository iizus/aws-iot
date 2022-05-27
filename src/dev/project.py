from client import Client

import certs


class Project:
    def __init__(self, endpoint:str, name:str='test') -> None:
        self.__name = name


    def create_client_using(self, certs_dir:str='') -> Client:
        client_id:str = certs_dir is None ? self.__name : certs_dir
        certs_path:str = f'{self.__name}/{certs_dir}'
        client:Client = self.create_client(
            client_id = client_id,
            cert = certs.get_cert_path(certs_path),
            key = certs.get_key_path(certs_path),
        )
        return client