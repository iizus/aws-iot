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