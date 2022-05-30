from symtable import Function
from typing import Literal
from awscrt import mqtt

class Connection:
    def __init__(self, project_name:str, connection:mqtt.Connection) -> None:
        self.__project_name:str = project_name
        self.__connection:mqtt.Connection = connection
        self.client_id:str = connection.client_id


    def use_topic(
        self,
        name:str = None,
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False
    ):
        return Topic(self.__project_name, self.__connection, name, QoS, retain)


    def disconnect(self) -> dict:
        client_id:str = self.__connection.client_id
        print(f"[{client_id}] Disconnecting...")
        disconnect_result:dict = self.__connection.disconnect().result()
        print(f"[{client_id}] Disconnected and Result: {disconnect_result}")
        return disconnect_result



def print_recieved_message(topic:str, payload:str, dup:bool, qos:mqtt.QoS, retain:bool, **kwargs:dict) -> None:
    print(topic)
    print(payload)
    print(dup)
    print(qos)
    print(retain)
    print(kwargs)
    print(f"[] ")



import json

class Topic:
    def __init__(
        self,
        project_name:str,
        connection:mqtt.Connection,
        name:str = None,
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False
    ) -> None:
        self.client_id:str = connection.client_id
        self.__topic:str = f"{project_name}/{self.client_id}" if name is None else name
        self.__connection:mqtt.Connection = connection
        self.__endpoint:str = f"{connection.host_name}:{connection.port}/{self.__topic}"
        self.__QoS:Literal = QoS
        self.__retain:bool = retain
        print(f"[{self.client_id}] Set topic as {self.__topic} by QoS{self.__QoS} and Retain message: {self.__retain}")


    def publish(self, message:dict={'message': 'test'}) -> int:
        payload:str = json.dumps(message)
        print(f"[{self.client_id}] Publishing... {payload} to {self.__endpoint} by QoS{self.__QoS} and Retain message: {self.__retain}")
        _, packet_id = self.__connection.publish(self.__topic, payload, self.__QoS, self.__retain)
        print(f"[{self.client_id}] Published {payload} to {self.__endpoint} by QoS{self.__QoS}, Retain message: {self.__retain} and Packet ID: {packet_id}")
        return packet_id


    def subscribe(self, callback:Function=print_recieved_message) -> dict:
        print(f"[{self.client_id}] Subscribing... {self.__endpoint} by QoS{self.__QoS} and Callback: {callback.__name__}")
        subscribe_future, packet_id = self.__connection.subscribe(
            self.__topic,
            self.__QoS,
            callback,
        )
        subscribe_result:dict = subscribe_future.result()
        topic:str = subscribe_result.get('topic')
        QoS:int = subscribe_result.get('qos')
        print(f"[{self.client_id}] Subscribed {self.__endpoint} Topic: {topic} by QoS{QoS}, Callback: {callback.__name__} and Packet ID: {packet_id}")
        return subscribe_result


    def unsubscribe(self) -> int:
        print(f"[{self.client_id}] Unsubscribing... {self.__endpoint}")
        _, packet_id = self.__connection.unsubscribe(self.__topic)
        print(f"[{self.client_id}] Unsubscribed {self.__endpoint} and Packet ID: {packet_id}")
        return packet_id