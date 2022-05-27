import certs, broker_util
from client import Client



class Broker:
    def __init__(self, env_name:str, region:str) -> None:
        '''
        >>> broker:Broker = Broker(env_name='test', region='us-east-1')
        '''
        self.__endpoint:str = broker_util.get_endpoint_from(
            config_path = 'endpoint.json',
            env_name = env_name,
            region = region,
        )
        self.__ca:str = certs.get_ca_path()


    def create_client_from(self, project_name:str='test', certs_dir:str='') -> Client:
        '''
        >>> broker:Broker = Broker(env_name='test', region='us-east-1')
        >>> client:Client = broker.create_client_from()
        '''
        certs_dir:str = f'{project_name}/{certs_dir}'
        client:Client = self.create_client(
            client_id = project_name,
            cert = certs.get_cert_path(certs_dir),
            key = certs.get_key_path(certs_dir),
        )
        return client


    def create_client(self, client_id:str, cert:str, key:str) -> Client:
        '''
        >>> broker:Broker = Broker(env_name='test', region='us-east-1')
        >>> client:Client = broker.create_client()
        '''
        client:Client = Client(
            endpoint = self.__endpoint,
            ca = self.__ca,
            client_id = client_id,
            cart = cert,
            key = key
        )
        print(f"""Creating client with 
            Client ID: {client_id},
            Cert: {cert},
            Key: {key}""")
        return client



if __name__ == '__main__':
    from doctest import testmod
    testmod()