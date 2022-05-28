# from topic import Topic

from typing import Literal
from awscrt import mqtt



class Connection:
    def __init__(self, connection:mqtt.Connection) -> None:
        self.__connection:mqtt.Connection = connection


    def use_topic(
        self,
        name:str = 'test/test',
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False
    ):
        return Topic(name, self.__connection, QoS, retain)


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
        name:str,
        connection:mqtt.Connection,
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False
    ) -> None:
        self.__topic:str = name
        self.__connection:mqtt.Connection = connection
        self.__endpoint:str = f"{connection.host_name}:{connection.port}/{name}"
        self.client_id:str = connection.client_id
        self.__QoS:Literal = QoS
        self.__retain:bool = retain


    def publish(self, message:dict) -> dict:
        payload:str = json.dumps(message)
        print(f"""Client ID: {self.client_id}
            publishing...
            Message: {payload} to
            Endpoint: {self.__endpoint}
            by QoS{self.__QoS}
            Retain: {self.__retain}""")
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
            Retain: {self.__retain}
            Result: {publish_result}""")
        return publish_result


    def subscribe(self, callback) -> dict:
        # return response
        pass


    def unsubscribe(self) -> dict:
        # return response
        pass