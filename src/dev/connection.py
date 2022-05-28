# from topic import Topic

from awscrt import mqtt


class Connection:
    def __init__(self, connection:mqtt.Connection) -> None:
        self.__connection:mqtt.Connection = connection


    def use_topic(self, name:str='test/test'):
        return Topic(name, self.__connection)


    def disconnect(self) -> dict:
        client_id:str = self.__connection.client_id
        print(f"Disconnecting... client ID: {client_id}")
        disconnect_result:dict = self.__connection.disconnect().result()
        print(f"Disconnected client ID: {client_id} and result: {disconnect_result}")
        return disconnect_result


class Topic:
    def __init__(self, name:str, connection:Connection) -> None:
        self.__topic:str = name
        self.client_id:str = connection.client_id


    def publish(self, message:dict) -> dict:
        # return response
        # pass
        print(message)


    def subscribe(self, callback) -> dict:
        # return response
        pass


    def unsubscribe(self) -> dict:
        # return response
        pass