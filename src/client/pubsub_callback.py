import json
from threading import Event
from src.utils import util
from src.client.account import get_endpoint, Endpoint
from src.client.connection import Topic, Connection


class PubSub_callback:
    from awscrt import mqtt
    from src.client.client import Client

    DEFAULT:dict = util.load_json('default.json')

    def __init__(
        self,
        endpoint:Endpoint = get_endpoint(),
        topic_name:str = DEFAULT.get('TOPIC_NAME'),
    ) -> None:
        self.__endpoint:Endpoint = endpoint
        self.__topic_name:str = topic_name


    def excute_callback_on(self, client:Client, callback, publisher:Client=None):
        connection:Connection = client.connect_to(self.__endpoint)
        result = callback(
            publisher = publisher,
            topic = connection.use_topic(self.__topic_name),
        )
        client.disconnect()
        return result

            
    def subscribe_and_wait_massage(self, publisher:Client, topic:Topic) -> None:
        self.__received_event:Event = Event()
        topic.subscribe(callback=self.__on_message_received)
        util.print_log(
            subject = topic.client_id,
            verb = 'Waiting...',
            message = "for all messages to be received"
        )
        self.excute_callback_on(client=publisher, callback=self.publish)
        self.__received_event.wait()


    def publish(self, publisher:Client, topic:Topic) -> int:
        self.__message:str = {'from': topic.client_id}
        packet_id:int = topic.publish(self.__message)
        return packet_id


    def __on_message_received(
        self,
        topic:str,
        payload:str,
        dup:bool,
        qos:mqtt.QoS,
        retain:bool,
        **kwargs:dict
    ) -> None:
        Topic.print_recieved_message(topic, payload, dup, qos, retain, **kwargs)
        decoded_payload:dict = json.loads(payload.decode('utf-8'))
        if self.__message == decoded_payload:
            self.__received_event.set()
        else:
            print(self.__message)
            print(decoded_payload)