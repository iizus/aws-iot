import sys
from uuid import uuid4
from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder


class MQTT:
    def __init__(self, endpoint:str) -> None:
        self.__endpoint:str = endpoint


    def connect_with(
        self,
        cert:str,
        key:str,
        ca:str,
        client_id:str = str(uuid4()),
    ) -> None:
        connection:mqtt.Connection = self.__create_connection_with(
            client_id,
            cert,
            key,
            ca
        )
        future:Future = connection.connect()
        # Wait for connection to be fully established.
        # Note that it's not necessary to wait, commands issued to the
        # mqtt_connection before its fully connected will simply be queued.
        # But this sample waits here so it's obvious when a connection
        # fails or succeeds.
        future.result()
        print("Connected!")
        return connection


    def disconnect(self, connection:mqtt.Connection) -> None:
        print("Disconnecting...")
        disconnect_future = connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")


    def __create_connection_with(
        self,
        client_id:str,
        cert:str,
        key:str,
        ca:str,
    ) -> mqtt.Connection:
        # Spin up resources
        event_loop_group:io.EventLoopGroup = io.EventLoopGroup(1)
        host_resolver:io.DefaultHostResolver = io.DefaultHostResolver(event_loop_group)

        connection:mqtt.Connection = mqtt_connection_builder.mtls_from_path(
            endpoint = self.__endpoint,
            cert_filepath = cert,
            pri_key_filepath = key,
            client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver),
            ca_filepath = ca,
            client_id = client_id,
            on_connection_interrupted = self.__on_connection_interrupted,
            on_connection_resumed = self.__on_connection_resumed,
            clean_session = False,
            keep_alive_secs = 30,
            http_proxy_options = None,
        )
        print(f"Connecting to {self.__endpoint} with client ID '{client_id}'...")
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


    def __on_resubscribe_complete(self, future:Future) -> None:
        results = future.result()
        print(f"Resubscribe results: {results}")
        for topic, qos in results.get('topics'):
            if qos is None: sys.error(f"Server rejected resubscribe to topic: {topic}")


    # Callback when connection is accidentally lost.
    def __on_connection_interrupted(self, error) -> None:
        print(f"Connection interrupted. Error: {error}")


def get_config(file_path:str='config.json') -> dict:
    with open(file_path) as config_file:
        from json import load
        config:dict = load(config_file)
        return config


if __name__ == '__main__':
    config:dict = get_config()
    client:MQTT = MQTT(endpoint=config.get('endpoint'))

    folder:str = 'certs'
    cert:str = f'{folder}/client.pem'

    connection:mqtt.Connection = client.connect_with(
        cert = f'{cert}.crt',
        key = f'{cert}.key',
        ca = f'{folder}/AmazonRootCA1.pem',
    )
    client.disconnect(connection)