from threading import Event
from src.utils import util
from src.client.account import get_endpoint, Endpoint
from src.client.connection import Topic, Connection
from src.fleet_provisioning.util import get_current_time

from src.client.endpoint import Provisioning


DEFAULT:dict = util.load_json('default.json')

def check_communication(
    account_name:str = DEFAULT.get('ACCOUNT_NAME'),
    region_name:str = DEFAULT.get('REGION_NAME'),
    template_name:str = DEFAULT.get('TEMPLATE_NAME'),
    thing_name_key:str = DEFAULT.get('THING_NAME_KEY'),
    topic_name:str = DEFAULT.get('TOPIC_NAME'),
):
    pubsub:PubSub = PubSub(
        endpoint = get_endpoint(account_name, region_name),
        template_name = template_name,
        thing_name_key = thing_name_key,
        topic_name = topic_name,
    )
    result = pubsub.check_communication()
    return result


class PubSub:
    from awscrt import mqtt
    from src.client.client import Client

    def __init__(
        self,
        endpoint:Endpoint = get_endpoint(),
        template_name:str = DEFAULT.get('TEMPLATE_NAME'),
        thing_name_key:str = DEFAULT.get('THING_NAME_KEY'),
        topic_name:str = DEFAULT.get('TOPIC_NAME'),
    ) -> None:
        # self.__endpoint:Endpoint = endpoint.set_FP(template_name, thing_name_key)
        self.__endpoint:Endpoint = endpoint
        self.__fp:Provisioning = Provisioning(endpoint, template_name, thing_name_key)
        self.__topic_name:str = topic_name


    def publish(self, publisher_name:str=get_current_time()):
        result = self.excute_callback_on(
            client = self.__fp.provision_thing(publisher_name),
            callback = self.__publish,
        )
        return result


    def check_communication(
        self,
        publisher_name:str = get_current_time(),
        subscriber_name:str = get_current_time(),
    ):
        result = self.check_communication_between(
            publisher = self.__fp.provision_thing(publisher_name),
            subscriber = self.__fp.provision_thing(subscriber_name),
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


    def excute_callback_on(self, client:Client, callback, publisher:Client=None):
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