# from topic import Topic

from typing import Literal
from awscrt import mqtt



class Connection:
    def __init__(self, project_name:str, connection:mqtt.Connection) -> None:
        self.__project_name:str = project_name
        self.__connection:mqtt.Connection = connection
        self.client_id:str = connection.client_id
        self.__endpoint:str = f"{connection.host_name}:{connection.port}"


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

    
    def resubscribe_all_topics(self):
        print(f"""Client ID: {self.client_id}
            resubscribing...
            Endpoint: {self.__endpoint}""")
        resubscribe_future, packet_id = self.__connection.resubscribe_existing_topics()
        print(f"""Client ID: {self.client_id}
            resubscribed
            Endpoint: {self.__endpoint}
            Packet ID: {packet_id}""")
        print(resubscribe_future.result())



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


    def publish(self, message:dict={'message': 'test'}) -> int:
        payload:str = json.dumps(message)
        print(f"""Client ID: {self.client_id}
            publishing...
            Message: {payload} to
            Endpoint: {self.__endpoint}
            by QoS{self.__QoS}
            Retain message: {self.__retain}""")
        _, packet_id = self.__connection.publish(self.__topic, payload, self.__QoS, self.__retain)
        print(f"""Client ID: {self.client_id}
            published
            Message: {payload} to
            Endpoint: {self.__endpoint}
            by QoS{self.__QoS}
            Retain message: {self.__retain}
            Packet ID: {packet_id}""")
        return packet_id


    def subscribe(self, callback) -> dict:
        print(f"""Client ID: {self.client_id}
            subscribing...
            Endpoint: {self.__endpoint}
            by QoS{self.__QoS}
            Callback: {callback.__name__}""")
        subscribe_future, packet_id = self.__connection.subscribe(
            self.__topic,
            self.__QoS,
            callback
        )
        subscribe_result:dict = subscribe_future.result()
        print(f"""Client ID: {self.client_id}
            subscribed
            Endpoint: {self.__endpoint}
            Topic: {subscribe_result.get('topic')}
            by QoS{subscribe_result.get('qos')}
            Callback: {callback.__name__}
            Packet ID: {packet_id}""")
        return subscribe_result


    def unsubscribe(self) -> int:
        print(f"""Client ID: {self.client_id}
            unsubscribing...
            Endpoint: {self.__endpoint}""")
        _, packet_id = self.__connection.unsubscribe(self.__topic)
        print(f"""Client ID: {self.client_id}
            unsubscribed
            Endpoint: {self.__endpoint}
            Packet ID: {packet_id}""")
        return packet_id