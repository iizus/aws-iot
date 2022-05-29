from connection import Connection

from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path



class Client:
    __event_loop_group:io.EventLoopGroup = io.EventLoopGroup(1)
    __host_resolver:io.DefaultHostResolver = io.DefaultHostResolver(__event_loop_group)
    client_bootstrap:io.ClientBootstrap = io.ClientBootstrap(__event_loop_group, __host_resolver)

    def __init__(self, project_name:str, id:str, cert:str, key:str) -> None:
        self.__project_name:str = project_name
        self.id:str = id
        self.cert:str = cert
        self.key:str = key

        
    def connect_to(self, endpoint, keep_alive:int=30, clean_session:bool=False) -> Connection:
        print(f"Connecting... client ID: {self.id}")
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
        print(f"Connected client ID: {self.id} and session present: {session_present}")
        return Connection(self.__project_name, connection)



from concurrent.futures import Future

# Callback when an interrupted connection is re-established.
def on_connection_resumed(
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
        resubscribe_future.add_done_callback(__on_resubscribe_complete)


def __on_resubscribe_complete(resubscribe_future:Future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe: {resubscribe_results}")
    topics = resubscribe_results.get('topics')
    for topic, QoS in topics:
        if QoS is None: exit(f"Server rejected resubscribe to {topic}")


# Callback when connection is accidentally lost.
def on_connection_interrupted(error) -> None:
    print(f"Connection interrupted. Error: {error}")