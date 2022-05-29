# from topic import Topic

from typing import Literal
from awscrt import mqtt



class Connection:
    def __init__(self, project_name:str, connection:mqtt.Connection) -> None:
        self.__project_name:str = project_name
        self.__connection:mqtt.Connection = connection


    def use_topic(
        self,
        name:str = None,
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False
    ):
        return Topic(self.__project_name, self.__connection, name, QoS, retain)


    def disconnect(self) -> dict:
        client_id:str = self.__connection.client_id
        print(f"Disconnecting... client ID: {client_id}")
        disconnect_result:dict = self.__connection.disconnect().result()
        print(f"Disconnected client ID: {client_id} and result: {disconnect_result}")
        return disconnect_result


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


    def publish(self, message:dict={'message': 'test'}) -> dict:
        payload:str = json.dumps(message)
        print(f"""Client ID: {self.client_id}
            publishing...
            Message: {payload} to
            Endpoint: {self.__endpoint}
            by QoS{self.__QoS}
            Retain message: {self.__retain}""")
        publish_future, _ = self.__connection.publish(
            self.__topic,
            payload,
            self.__QoS,
            self.__retain,
        )
        publish_result:dict = publish_future.result()
        print(f"""Client ID: {self.client_id}
            published
            Message: {payload} to
            Endpoint: {self.__endpoint}
            by QoS{self.__QoS}
            Retain message: {self.__retain}
            Packet ID: {publish_result.get('packet_id')}""")
        return publish_result


    def subscribe(self, callback) -> dict:
        print(f"""Client ID: {self.client_id}
            subscribing...
            Endpoint: {self.__endpoint}
            by QoS{self.__QoS}
            Callback: {callback.__name__}""")
        subscribe_future, _ = self.__connection.subscribe(self.__topic, self.__QoS, callback)
        subscribe_result:dict = subscribe_future.result()
        print(f"""Client ID: {self.client_id}
            subscribed
            Endpoint: {self.__endpoint}
            Topic: {subscribe_result.get('topic')}
            by QoS{subscribe_result.get('qos')}
            Callback: {callback.__name__}
            Packet ID: {subscribe_result.get('packet_id')}""")
        return subscribe_result


    def unsubscribe(self) -> dict:
        # return response
        pass