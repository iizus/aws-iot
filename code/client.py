import json
from concurrent.futures import Future
from awscrt import mqtt



class Client:
    default_topic:str = 'test/test'
    default_payload:dict = {'message': 'test'}

    def __init__(self, connection:mqtt.Connection) -> None:
        self.client_id = connection.client_id
        self.__connection = connection


    def subscribe(
        self,
        callback,
        topic:str = default_topic,
        QoS:int = mqtt.QoS.AT_MOST_ONCE,
    ) -> dict:
        print(f"Subscribing {topic}")
        subscribe_future, _ = self.__connection.subscribe(topic, QoS, callback)
        subscribe_result:dict = subscribe_future.result()
        print(f"Subscribed: {subscribe_result}")
        return subscribe_result


    def publish(
        self,
        topic:str = default_topic,
        payload:dict = default_payload,
        QoS = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False,
    ) -> dict:
        payload:json = json.dumps(payload)
        print(f"Publishing {payload} to {topic} by QoS{QoS}")
        publish_future, _ = self.__connection.publish(topic, payload, QoS, retain)
        publish_result:dict = publish_future.result()
        print(f"Published: {publish_result}")
        return publish_result


    def disconnect(self) -> dict:
        print("Disconnecting...")
        disconnect_future:Future = self.__connection.disconnect()
        disconnect_result:dict = disconnect_future.result()
        print(f"Disconnected: {disconnect_result}")
        return disconnect_result



if __name__ == '__main__':
    None