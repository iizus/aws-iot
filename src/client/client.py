from src.utils import util
from src.client.certs import Cert
from src.client.connection import Connection
from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path

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
        port:str = f"{endpoint.name}:{endpoint.port}"
        self.__print_log(verb='Connecting...', message=f"to {port}, Keep alive: {keep_alive} and Clean session: {clean_session}")
        connection:mqtt.Connection = mtls_from_path(
            endpoint = endpoint.name,
            ca_filepath = endpoint.ca,
            client_id = self.id,
            cert_filepath = self.cert,
            pri_key_filepath = self.key,
            client_bootstrap = self.client_bootstrap,
            on_connection_interrupted = on_connection_interrupted,
            on_connection_resumed = on_connection_resumed,
            clean_session = clean_session,
            keep_alive_secs = keep_alive,
            port = endpoint.port,
            http_proxy_options = endpoint.proxy,
        )
        # Wait for connection to be fully established.
        # Note that it's not necessary to wait, commands issued to the
        # mqtt_connection before its fully connected will simply be queued.
        # But this sample waits here so it's obvious when a connection
        # fails or succeeds.
        connect_result:dict = connection.connect().result()
        session_present:bool = connect_result.get('session_present')
        self.__print_log(verb='Connected', message=f"to {port}, Keep alive: {keep_alive}, Clean session: {clean_session} and Session present: {session_present}")
        return Connection(self.__project_name, connection)


    def __print_log(self, verb:str, message:str) -> None:
        util.print_log(subject=self.id, verb=verb, message=message)



from typing import List
from concurrent.futures import Future

# Callback when an interrupted connection is re-established.
def on_connection_resumed(
    connection:mqtt.Connection,
    return_code,
    session_present
) -> None:
    print(f"[{connection.client_id}] Resumed connection with {connection.host_name}, Return code: {return_code} and Session present: {session_present}")
    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        packet_id:int = __resubscribe(connection)
        

def __resubscribe(connection:mqtt.Connection) -> int:
    client_id:str = connection.client_id
    endpoint:str = connection.host_name
    print("Session did not persist. Resubscribing to existing topics...")
    util.print_log(subject=client_id, verb='Resubscribing...', message=f"Endpoint: {endpoint}")
    resubscribe_future, packet_id = connection.resubscribe_existing_topics()
    # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
    # evaluate result with a callback instead.
    resubscribe_future.add_done_callback(__on_resubscribe_complete)
    util.print_log(subject=client_id, verb='Resubscribed', message=f"Endpoint: {endpoint} Packet ID: {packet_id}")
    return packet_id


def __on_resubscribe_complete(resubscribe_future:Future) -> None:
    resubscribe_results = resubscribe_future.result()
    topics:List[str] = resubscribe_results.get('topics')
    packet_id:int = resubscribe_results.get('packet_id')
    print(f"Resubscribe: {resubscribe_results}")
    for topic, QoS in topics:
        if QoS is None: exit(f"Server rejected resubscribe to {topic}")


# Callback when connection is accidentally lost.
def on_connection_interrupted(error) -> None:
    print(f"Connection interrupted. Error: {error}")



class Project:
    def __init__(self, name:str='test') -> None:
        self.__name:str = name


    def create_client(self, client_id:str='client1', cert_dir:str='') -> Client:
        cert_dir:str = f'{self.__name}/{cert_dir}{client_id}'
        return Client(
            project_name = self.__name,
            id = self.__name if client_id == '' else client_id,
            cert = Cert(cert_dir)
        )