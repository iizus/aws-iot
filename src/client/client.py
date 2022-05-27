# import json
# from concurrent.futures import Future
# from awscrt import mqtt


from multiprocessing import connection
import certs, broker_util
from client import Client
from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path

from client.connection import Connection



class Client:
    def __init__(self, endpoint:str, ca:str, client_id:str, cert:str, key:str) -> None:
        self.__endpoint:str = endpoint
        self.__ca:str = ca
        self.__client_id:str = client_id
        self.__cert_path:str = cert
        self.__key_path:str = key
        self.__connection:mqtt.Connection = self.__create_connection_with(client_id, cert, key)
        connection:Connection = Connection(self.__connection)


    def connect(self) -> Connection:
        '''
        >>> broker:Broker = Broker(env_name='test', region='us-east-1')
        >>> client:Client = broker.create_client_from()
        Connecting to a7chvrvs7m8go-ats.iot.us-east-1.amazonaws.com with 
                    Client ID: test,
                    Cert: certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-certificate.pem.crt,
                    Key: certs/test/ad1b473789e53248ecd36eb7e6a888755d17bf21318b3fb3ca8bf79cbb636055-private.pem.key
        Connected: {'session_present': True}
        '''
        connect_future:Future = self.__connection.connect()
        # Wait for connection to be fully established.
        # Note that it's not necessary to wait, commands issued to the
        # mqtt_connection before its fully connected will simply be queued.
        # But this sample waits here so it's obvious when a connection
        # fails or succeeds.
        connect_result:dict = connect_future.result()
        print(f"Connected: {connect_result}")
        # return connec


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