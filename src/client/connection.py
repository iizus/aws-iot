from typing import Literal, List
from awscrt import mqtt
from src.client.topic import Topic


class Connection:
    def __init__(self, project_name:str, connection:mqtt.Connection) -> None:
        self.__project_name:str = project_name
        self.connection:mqtt.Connection = connection
        self.client_id:str = connection.client_id
        self.__topics:List[Topic] = list()


    def use_topic(
        self,
        name:str = None,
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False,
    ) -> Topic:
        self.__topic:Topic = Topic(self.__project_name, self.connection, name, QoS, retain)
        self.__topics.append(self.__topic)
        return self.__topic


    def disconnect(self) -> dict:
        for topic in self.__topics:
            topic.unsubscribe()
        else:
            disconnect_result:dict = self.connection.disconnect().result()
            return disconnect_result