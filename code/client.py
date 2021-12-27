import sys
from uuid import uuid4
from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder


def read_config(file_path:str='config.json') -> dict:
    with open(file_path) as config_file:
        from json import load
        config:dict = load(config_file)
        return config


class Client:
    def __init__(self, endpoint:str, ca:str) -> None:
        self.__endpoint:str = endpoint
        self.__ca:str = ca

    def connect(self, cert:str, key:str, client_id:str=str(uuid4())) -> mqtt.Connection:
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
        connect_future.result()
        print("Connected!")
        return self.__connection

    def publish(
        self,
        topic:str = 'test/test',
        payload:dict = "{'message': 'test'}",
        QoS:mqtt.QoS = mqtt.QoS.AT_MOST_ONCE
    ) -> None:
        print(f"Publishing {payload} to {topic} by {QoS}")
        future, _ = self.__connection.publish(topic, payload, QoS)
        print(future)
        print(f"Published {payload} to {topic} by {QoS}")

    def subscribe(
        self,
        callback,
        topic:str = 'test/test',
        QoS:int = mqtt.QoS.AT_MOST_ONCE,
    ) -> None:
        print(f"Subscribing {topic}")
        subscribe_future, _ = self.__connection.subscribe(topic, QoS, callback)
        subscribe_result = subscribe_future.result()
        print(f"Subscribed {topic}")
        print(subscribe_result)

    def disconnect(self) -> None:
        print("Disconnecting...")
        disconnect_future:Future = self.__connection.disconnect()
        disconnect_result = disconnect_future.result()
        print("Disconnected!")
        return disconnect_result

    def __create_connection_with(
        self,
        client_id:str,
        cert:str,
        key:str,
    ) -> mqtt.Connection:
        event_loop_group:io.EventLoopGroup = io.EventLoopGroup(1)
        host_resolver:io.DefaultHostResolver = io.DefaultHostResolver(event_loop_group)

        connection:mqtt.Connection = mqtt_connection_builder.mtls_from_path(
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

    def __on_resubscribe_complete(self, future:Future) -> None:
        results = future.result()
        print(f"Resubscribe results: {results}")
        for topic, qos in results.get('topics'):
            if qos is None: sys.error(f"Server rejected resubscribe to topic: {topic}")

    # Callback when connection is accidentally lost.
    def __on_connection_interrupted(self, error) -> None:
        print(f"Connection interrupted. Error: {error}")

    def __on_resubscribe_complete(self, resubscribe_future:Future):
        resubscribe_results = resubscribe_future.result()
        print(f"Resubscribe results: {resubscribe_results}")
        topics = resubscribe_results.get('topics')
        for topic, QoS in topics:
            if QoS is None:
                sys.exit(f"Server rejected resubscribe to topic: {topic}")


if __name__ == '__main__':
    config:dict = read_config()
    folder:str = 'certs'
    cert:str = f'{folder}/client.pem'

    from threading import Event
    received_event = Event()

    def on_message_received(topic:str, payload:dict, dup, qos, retain, **kwargs) -> None:
        print(f"Received {payload} from {topic}")
        received_event.set()

    client:Client = Client(
        endpoint = config.get('endpoint'),
        ca = f'{folder}/AmazonRootCA1.pem',
    )
    client.connect(f'{cert}.crt', f'{cert}.key')
    client.subscribe(callback=on_message_received, QoS=mqtt.QoS.AT_LEAST_ONCE)
    client.publish(QoS=mqtt.QoS.AT_LEAST_ONCE)
    print("Waiting for all messages to be received...")
    received_event.wait()
    client.disconnect()