from topic import Topic

from awscrt import mqtt
from concurrent.futures import Future


class Connection:
    def __init__(self, connection:mqtt.Connection) -> None:
        self.__connection:mqtt.Connection = connection


    def use_topic(self, name:str='test/test') -> Topic:
        return Topic(name)


    def disconnect(self) -> dict:
        client_id:str = self.__connection.client_id
        print(f"Disconnecting... client ID: {client_id}")
        disconnect_future:Future = self.__connection.disconnect()
        disconnect_result:dict = disconnect_future.result()
        print(f"Disconnected client ID: {client_id} and result: {disconnect_result}")
        return disconnect_result