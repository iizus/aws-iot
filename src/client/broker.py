import certs, broker_util
from client import Client
from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path



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

    
    def connect_for(self, project_name:str='test', certs_dir:str='') -> Client:
        '''
        >>> broker:Broker = Broker(env_name='test', region='us-east-1')
        >>> client:Client = broker.connect_for()
        Connecting to a7chvrvs7m8go-ats.iot.us-east-1.amazonaws.com with 
                    Client ID: test,
                    Cert: certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt,
                    Key: certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key
        Connected: {'session_present': True}
        '''
        certs_dir:str = f'{project_name}/{certs_dir}'
        client:Client = self.connect(
            cert = certs.get_cert_path(certs_dir),
            key = certs.get_key_path(certs_dir),
            client_id = project_name,
        )
        return client


    def connect(self, cert:str, key:str, client_id:str) -> Client:
        print(f"""Connecting to {self.__endpoint} with 
            Client ID: {client_id},
            Cert: {cert},
            Key: {key}""")
        connection:mqtt.Connection = self.__create_connection_with(client_id, cert, key)
        connect_future:Future = connection.connect()
        # Wait for connection to be fully established.
        # Note that it's not necessary to wait, commands issued to the
        # mqtt_connection before its fully connected will simply be queued.
        # But this sample waits here so it's obvious when a connection
        # fails or succeeds.
        connect_result:dict = connect_future.result()
        client:Client = Client(connection)
        print(f"Connected: {connect_result}")
        return client


    def __create_connection_with(
        self,
        client_id:str,
        cert:str,
        key:str,
    ) -> mqtt.Connection:
        event_loop_group:io.EventLoopGroup = io.EventLoopGroup(1)
        host_resolver:io.DefaultHostResolver = io.DefaultHostResolver(event_loop_group)
        
        connection:mqtt.Connection = mtls_from_path(
            endpoint = self.__endpoint,
            cert_filepath = cert,
            pri_key_filepath = key,
            client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver),
            ca_filepath = self.__ca,
            client_id = client_id,
            on_connection_interrupted = broker_util.on_connection_interrupted,
            on_connection_resumed = broker_util.on_connection_resumed,
            clean_session = False,
            keep_alive_secs = 30,
            http_proxy_options = None,
        )
        return connection



if __name__ == '__main__':
    from doctest import testmod
    testmod()