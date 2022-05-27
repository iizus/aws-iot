from topic import Topic

from awscrt import mqtt



class Connection:
    def __init__(self, connection:mqtt.Connection) -> None:
        self.__connection:mqtt.Connection = connection


    def use_topic(self, name:str='test/test') -> Topic:
        return Topic(name)


    def disconnect(self) -> dict:
        return response