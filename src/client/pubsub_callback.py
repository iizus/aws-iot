from threading import Event
from src.utils import util
from src.client.account import get_endpoint, Endpoint
from src.client.connection import Topic, Connection
from src.fleet_provisioning.provisioning import Provisioning
from src.fleet_provisioning.util import get_current_time


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
        connection.disconnect()
        return result

            
    def subscribe(self, publisher:Client, topic:Topic) -> int:
        self.__received_event:Event = Event()
        topic.subscribe(callback=self.__on_message_received)
        self.excute_callback_on(client=publisher, callback=self.publish)
        util.print_log(
            subject = topic.client_id,
            verb = 'Waiting...',
            message = "for all messages to be received"
        )
        self.__received_event.wait()
        packet_id:int = topic.unsubscribe()
        return packet_id


    def publish(self, publisher:Client, topic:Topic) -> int:
        packet_id:int = topic.publish({'from': topic.client_id})
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
        self.__received_event.set()