from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

import certs
from client import Client
from sys import exit
from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path
from utils.util import load_json



class Broker:
    def __init__(self, env_name:str, region:str) -> None:
        self.__endpoint:str = self.__get_endpoint_from(
            config_path = 'endpoint.json',
            env_name = env_name,
            region = region,
        )
        self.__ca:str = certs.get_ca_path()

    
    def connect_for(self, project_name:str='test') -> Client:
        client:Client = self.connect(
            cert = certs.get_cert_path_of(project_name),
            key = certs.get_key_path_of(project_name),
            client_id = project_name,
        )
        return client


    def connect(self, cert:str, key:str, client_id:str) -> Client:
        print(f"""Connecting to 
            Endpoint: {self.__endpoint} with 
            Client ID: {client_id},
            Cert: {cert},
            Key: {key}
        """)
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


    def __get_endpoint_from(self, config_path:str='endpoint.json', env_name:str='test', region:str='us-east-1') -> str:
        endpoints:dict = load_json(config_path)
        endpoint:str = endpoints.get(env_name)
        endpoint:str = f'{endpoint}-ats.iot.{region}.amazonaws.com'
        return endpoint


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
            on_connection_interrupted = self.__on_connection_interrupted,
            on_connection_resumed = self.__on_connection_resumed,
            clean_session = False,
            keep_alive_secs = 30,
            http_proxy_options = None,
        )
        return connection
    

    # Callback when an interrupted connection is re-established.
    def __on_connection_resumed(
        self,
        connection:mqtt.Connection,
        return_code,
        session_present
    ) -> None:
        print(f"Connection resumed. return code: {return_code} session present: {session_present}")

        if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
            print("Session did not persist. Resubscribing to existing topics...")
            resubscribe_future, _ = connection.resubscribe_existing_topics()
            # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
            # evaluate result with a callback instead.
            resubscribe_future.add_done_callback(self.__on_resubscribe_complete)


    def __on_resubscribe_complete(self, resubscribe_future:Future):
        resubscribe_results = resubscribe_future.result()
        print(f"Resubscribe: {resubscribe_results}")
        topics = resubscribe_results.get('topics')
        for topic, QoS in topics:
            if QoS is None: exit(f"Server rejected resubscribe to {topic}")


    # Callback when connection is accidentally lost.
    def __on_connection_interrupted(self, error) -> None:
        print(f"Connection interrupted. Error: {error}")



if __name__ == '__main__':
    from doctest import testmod
    testmod()