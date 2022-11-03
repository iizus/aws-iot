from typing import Literal
from awscrt import mqtt
from src.utils import util
from src.client.topic import Topic


class Connection:
    def __init__(self, project_name:str, connection:mqtt.Connection) -> None:
        self.__project_name:str = project_name
        self.connection:mqtt.Connection = connection
        self.client_id:str = connection.client_id


    def use_topic(
        self,
        name:str = None,
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False
    ):
        return Topic(self.__project_name, self.connection, name, QoS, retain)