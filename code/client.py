from email import message
import json
from sys import exit
from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path


def read_config(file_path:str='config.json') -> dict:
    with open(file_path) as config_file:
        from json import load
        config:dict = load(config_file)
        return config


def connect(endpoint:str, ca:str, client_id:str, client_cert:str) -> None:
    from threading import Event
    received_event:Event = Event()

    def on_message_received(topic:str, payload:dict, dup, qos, retain, **kwargs) -> None:
        print(f"Received {payload} from {topic}")
        received_event.set()

    client:Client = Client(endpoint, ca)
    client.connect(
        cert = f'{client_cert}.crt',
        key = f'{client_cert}.key',
        client_id = client_id,
    )
    client.subscribe(callback=on_message_received, QoS=mqtt.QoS.AT_LEAST_ONCE)
    client.publish(payload={'client_id': client_id}, QoS=mqtt.QoS.AT_LEAST_ONCE)
    print("Waiting for all messages to be received...")
    received_event.wait()
    client.disconnect()


class Client:
    def __init__(self, endpoint:str, ca:str) -> None:
        self.__endpoint:str = endpoint
        self.__ca:str = ca

    def connect(self, cert:str, key:str, client_id:str) -> mqtt.Connection:
        print(f"Connecting to {self.__endpoint} with client ID {client_id}")
        self.__connection:mqtt.Connection = self.__create_connection_with(
            client_id,
            cert,
            key,
        )
        connect_future:Future = self.__connection.connect()
        # Wait for connection to be fully established.
        # Note that it's not necessary to wait, commands issued to the
        # mqtt_connection before its fully connected will simply be queued.
        # But this sample waits here so it's obvious when a connection
        # fails or succeeds.
        connect_result:dict = connect_future.result()
        print(f"Connected: {connect_result}")
        return self.__connection

    def subscribe(self,
        callback,
        topic:str = 'test/test',
        QoS:int = mqtt.QoS.AT_MOST_ONCE,
    ) -> dict:
        print(f"Subscribing {topic}")
        subscribe_future, _ = self.__connection.subscribe(topic, QoS, callback)
        subscribe_result:dict = subscribe_future.result()
        print(f"Subscribed: {subscribe_result}")
        return subscribe_result

    def publish(self,
        topic:str = 'test/test',
        payload:dict = {'message': 'test'},
        QoS:mqtt.QoS = mqtt.QoS.AT_MOST_ONCE
    ) -> dict:
        payload:json = json.dumps(payload)
        print(f"Publishing {payload} to {topic} by QoS{QoS}")
        publish_future, _ = self.__connection.publish(topic, payload, QoS, retain=False)
        publish_result:dict = publish_future.result()
        print(f"Published: {publish_result}")
        return publish_result

    def disconnect(self) -> dict:
        print("Disconnecting...")
        disconnect_future:Future = self.__connection.disconnect()
        disconnect_result:dict = disconnect_future.result()
        print(f"Disconnected: {disconnect_result}")
        return disconnect_result

    def __create_connection_with(self,
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
    def __on_connection_resumed(self,
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
    config:dict = read_config()
    folder:str = 'certs'
    from uuid import uuid4
    connect(
        endpoint = config.get('endpoint'),
        ca = f'{folder}/AmazonRootCA1.pem',
        client_id = str(uuid4()),
        client_cert = f'{folder}/client.pem',
    )