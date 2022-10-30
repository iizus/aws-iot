from threading import Event
from src.utils import util
from src.client.client import Client
from src.client.endpoint import Endpoint
from src.client.connection import Topic, Connection


DEFAULT_TOPIC:str = 'check/communication'
DEFAULT_TEMPLATE_NAME:str = 'aws-iot'
DEFAULT_THING_NAME_KEY:str = 'device_id'


class PubSub:
    from awscrt import mqtt

    def __init__(
        self,
        endpoint:Endpoint,
        template_name:str = DEFAULT_TEMPLATE_NAME,
        thing_name_key:str = DEFAULT_THING_NAME_KEY,
        topic_name:str = DEFAULT_TOPIC,
    ) -> None:
        self.__endpoint:Endpoint = endpoint.set_FP(template_name, thing_name_key)
        self.__topic_name:str = topic_name


    def publish(self):
        result = self.excute_callback_on(
            client = self.__endpoint.provision_thing(),
            callback = self.__publish,
        )
        return result


    def check_communication(self):
        result = self.check_communication_between(
            publisher = self.__endpoint.provision_thing(),
            subscriber = self.__endpoint.provision_thing(),
        )
        return result


    def check_communication_between(self, publisher:Client, subscriber:Client):
        result = self.excute_callback_on(
            client = subscriber,
            callback = self.__subscribe,
            publisher = publisher,
        )
        return result

            
    def __subscribe(self, publisher:Client, topic:Topic) -> int:
        self.__received_event:Event = Event()
        topic.subscribe(callback=self.__on_message_received)
        self.excute_callback_on(client=publisher, callback=self.__publish)
        util.print_log(
            subject = topic.client_id,
            verb = 'Waiting...',
            message = "for all messages to be received"
        )
        self.__received_event.wait()
        packet_id:int = topic.unsubscribe()
        return packet_id


    def __publish(self, publisher:Client, topic:Topic) -> int:
        packet_id:int = topic.publish({'from': topic.client_id})
        return packet_id


    def excute_callback_on(self, client:Client, callback, publisher:Client = None):
        connection:Connection = client.connect_to(self.__endpoint)
        result = callback(
            publisher = publisher,
            topic = connection.use_topic(self.__topic_name),
        )
        connection.disconnect()
        return result


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