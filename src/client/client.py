from src.utils import util
from src.client.certs import Cert
from src.client.connection import Connection
from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path
from src.client import client_callback


class Client:
    __event_loop_group:io.EventLoopGroup = io.EventLoopGroup(1)
    __host_resolver:io.DefaultHostResolver = io.DefaultHostResolver(__event_loop_group)
    client_bootstrap:io.ClientBootstrap = io.ClientBootstrap(__event_loop_group, __host_resolver)

    def __init__(self, project_name:str, id:str, cert:Cert) -> None:
        self.__project_name:str = project_name
        self.id:str = id
        self.cert:str = cert.get_cert_path()
        self.key:str = cert.get_key_path()
        self.__print_log(verb='Created', message=f"client with Cert: {self.cert} and Key: {self.key}")

        
    def connect_to(self, endpoint, keep_alive:int=30, clean_session:bool=False) -> Connection:
        proxy = endpoint.proxy
        self.__print_log(
            verb = 'Connecting...',
            message = f"to {endpoint.endpoint}, Keep alive: {keep_alive} and Clean session: {clean_session}"
        )
        connection:mqtt.Connection = mtls_from_path(
            endpoint = endpoint.name,
            ca_filepath = endpoint.ca_path,
            client_id = self.id,
            cert_filepath = self.cert,
            pri_key_filepath = self.key,
            client_bootstrap = self.client_bootstrap,
            on_connection_interrupted = client_callback.on_connection_interrupted,
            on_connection_resumed = client_callback.on_connection_resumed,
            clean_session = clean_session,
            keep_alive_secs = keep_alive,
            port = endpoint.port,
            http_proxy_options = proxy,
        )
        # Wait for connection to be fully established.
        # Note that it's not necessary to wait, commands issued to the
        # mqtt_connection before its fully connected will simply be queued.
        # But this sample waits here so it's obvious when a connection
        # fails or succeeds.
        __connect = connection.connect()
        connect_result:dict = __connect.result()
        session_present:bool = connect_result.get('session_present')
        self.__print_log(verb='Connected', message=f"to {endpoint.endpoint}, Keep alive: {keep_alive}, Clean session: {clean_session} and Session present: {session_present}")
        return Connection(self.__project_name, connection)


    def __print_log(self, verb:str, message:str) -> None:
        util.print_log(subject=self.id, verb=verb, message=message)