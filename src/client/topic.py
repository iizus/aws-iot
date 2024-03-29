import json
from typing import Literal
from awscrt import mqtt
from src.utils import util


class Topic:
    def print_recieved_message(
        topic:str,
        payload:str,
        dup:bool,
        qos:mqtt.QoS,
        retain:bool,
        **kwargs:dict
    ) -> None:
        message:dict = json.loads(payload)
        util.print_log(subject=topic, verb='Recieved', message=f"{message} by QoS{qos}, DUP: {dup} and Retain message: {retain}")


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
        util.print_log(
            subject = self.client_id,
            verb = 'Set',
            message = f"topic as {self.__topic} by QoS{self.__QoS} and Retain message: {self.__retain}"
        )


    def publish(self, message:dict={'message': 'test'}) -> int:
        payload:str = json.dumps(message)
        self.__print_publish_log(verb='Publishing...', payload=payload)
        _, packet_id = self.__connection.publish(
            self.__topic,
            payload,
            self.__QoS,
            self.__retain
        )
        self.__print_publish_log(verb='Published', payload=payload, packet_id=packet_id)
        return packet_id


    def subscribe(self, callback=print_recieved_message) -> dict:
        self.__print_subscribe_log(verb='Subscribing...', QoS=self.__QoS, callback_name=callback.__name__)
        subscribe_future, packet_id = self.__connection.subscribe(
            self.__topic,
            self.__QoS,
            callback,
        )
        subscribe_result:dict = subscribe_future.result()
        # topic:str = subscribe_result.get('topic')
        QoS:int = subscribe_result.get('qos')
        self.__print_subscribe_log(verb='Subscribed', QoS=QoS, callback_name=callback.__name__, packet_id=packet_id)
        return subscribe_result


    def unsubscribe(self) -> int:
        self.__print_unsubscribe_log(verb='Unsubscribing...')
        _, packet_id = self.__connection.unsubscribe(self.__topic)
        self.__print_unsubscribe_log(verb='Unsubscribed', packet_id=packet_id)
        return packet_id


    def __print_publish_log(self, verb:str, payload:str, packet_id:int=None) -> None:
        message:str = f"{payload} to {self.__endpoint} by QoS{self.__QoS}, Retain message: {self.__retain}"
        self.__print_pubsub_log(verb, message, packet_id)


    def __print_subscribe_log(self, verb:str, QoS:Literal, callback_name:str, packet_id:int=None) -> None:
        self.__print_pubsub_log(verb=verb, message=f"{self.__endpoint} by QoS{QoS}, Callback: {callback_name}", packet_id=packet_id)


    def __print_unsubscribe_log(self, verb:str, packet_id:int=None) -> None:
        self.__print_pubsub_log(verb=verb, message=self.__endpoint, packet_id=packet_id)


    def __print_pubsub_log(self, verb:str, message:str, packet_id:int=None) -> None:
        self.__print_log(verb, f"{message} and Packet ID: {packet_id}")


    def __print_log(self, verb:str, message:str) -> None:
        util.print_log(subject=self.client_id, verb=verb, message=message)