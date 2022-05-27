from topic import Topic

from concurrent.futures import Future
from awscrt import io, mqtt
from awsiot.mqtt_connection_builder import mtls_from_path



class Connection:
    def __init__(self, endpoint:str, ca:str, client_id:str, cert:str, key:str) -> None:
        pass
        # self.__connection:mqtt.Connection = self.__create_connection_with(client_id, cert, key)


    def use_topic(self, name:str='test/test') -> Topic:
        return Topic(name)


    def disconnect(self) -> dict:
        return response