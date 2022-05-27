from connection import Connection
import certs



class Client:
    def __init__(self, endpoint:str, client_id:str, certs_path:str) -> None:
        self.__endpoint:str = endpoint
        self.__client_id:str = client_id
        self.__ca:str = certs.get_ca_path()
        self.__cert:str = certs.get_cert_path(certs_path)
        self.__key:str = certs.get_key_path(certs_path)
        # print(f"""Creating client with 
        #     Client ID: {client_id},
        #     Cert: {cert},
        #     Key: {key}""")


    def connect(self) -> Connection:
        connection:Connection = Connection(
            endpoint = self.__endpoint,
            ca = self.__ca,
            client_id = self.__client_id,
            cert = self.__cert,
            key = self.__key,
        )
        return connection