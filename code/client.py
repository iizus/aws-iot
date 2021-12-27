from uuid import uuid4
from awscrt import mqtt
from mqtt import MQTT, get_config


class Client:
    def __init__(self, endpoint:str, ca:str) -> None:
        self.__mqtt:MQTT = MQTT(endpoint, ca)

    def connect(self, cert:str, key:str, client_id:str=str(uuid4)) -> None:
        self.__connection:mqtt.Connection = self.__mqtt.connect_with(cert, key, client_id)

    def publish(
        self,
        topic:str = 'test/test',
        payload:dict = "{'message': 'test'}",
        QoS:int = mqtt.QoS.AT_MOST_ONCE
    ) -> None:
        print(f"Publishing message to topic '{topic}': {message}")
        self.__connection.publish(topic, payload, QoS)
        print(f"Published message to topic '{topic}': {message}")

    def subscribe(
        self,
        callback,
        topic:str = 'test/test',
        QoS:int = mqtt.QoS.AT_MOST_ONCE,
    ) -> None:
        print(f"Subscribing to topic '{topic}'...")
        subscribe_future, _ = self.__connection.subscribe(topic, QoS, callback)
        subscribe_result = subscribe_future.result()
        # print(f"Subscribed with QoS{subscribe_result.get('qos')}")
        print(subscribe_result)

    def disconnect(self) -> None:
        self.__mqtt.disconnect(self.__connection)


if __name__ == '__main__':
    config:dict = get_config()
    folder:str = 'certs'

    def on_message_received(topic:str, payload:dict, dup, qos, retain, **kwargs) -> None:
        print(f"Received message from topic '{topic}': {payload}")

    client:Client = Client(
        endpoint = config.get('endpoint'),
        ca = f'{folder}/AmazonRootCA1.pem',
    )

    cert:str = f'{folder}/client.pem'
    client.connect(
        cert = f'{cert}.crt',
        key = f'{cert}.key',
    )

    client.subscribe(callback=on_message_received, QoS=mqtt.QoS.AT_LEAST_ONCE)

    from time import sleep
    import json

    publish_count:int = 1
    while publish_count <= 3:
        message:str = f"test [{publish_count}]"
        client.publish(payload=json.dumps(message), QoS=mqtt.QoS.AT_LEAST_ONCE)
        sleep(3)
        publish_count += 1
    
    client.disconnect()