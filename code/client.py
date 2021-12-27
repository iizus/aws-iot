from uuid import uuid4
from awscrt import mqtt
from mqtt import MQTT, get_config


class Client:
    def __init__(self, endpoint:str, ca:str) -> None:
        self.__mqtt:MQTT = MQTT(endpoint, ca)

    def connect(self, cert:str, key:str, client_id:str=str(uuid4())) -> None:
        self.__connection:mqtt.Connection = self.__mqtt.connect_with(cert, key, client_id)

    def publish(
        self,
        topic:str = 'test/test',
        payload:dict = "{'message': 'test'}",
        QoS:mqtt.QoS = mqtt.QoS.AT_MOST_ONCE
    ) -> None:
        print(f"Publishing {payload} to {topic} by {QoS}")
        future = self.__connection.publish(topic, payload, QoS)
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
        self.__mqtt.disconnect(self.__connection)


if __name__ == '__main__':
    config:dict = get_config()
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