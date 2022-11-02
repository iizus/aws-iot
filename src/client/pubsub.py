from typing import List
from src.utils import util
from src.client.account import get_endpoint, Endpoint
from src.client.connection import Connection
from src.client.pubsub_callback import PubSub_callback
from src.fleet_provisioning.provisioning import Provisioning, get_current_time


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
    from src.client.client import Client

    def __init__(
        self,
        endpoint:Endpoint = get_endpoint(),
        template_name:str = DEFAULT.get('TEMPLATE_NAME'),
        thing_name_key:str = DEFAULT.get('THING_NAME_KEY'),
        topic_name:str = DEFAULT.get('TOPIC_NAME'),
    ) -> None:
        self.__endpoint:Endpoint = endpoint
        self.__callback:PubSub_callback = PubSub_callback(endpoint, topic_name)
        self.__provisioning:Provisioning = Provisioning(endpoint, template_name, thing_name_key)


    def publish(self, publisher_name:str=get_current_time()):
        result = self.__callback.excute_callback_on(
            client = self.__provisioning.provision_thing(publisher_name),
            callback = self.__callback.publish,
        )
        return result


    def check_communication(
        self,
        publisher_name:str = get_current_time(),
        subscriber_name:str = get_current_time(),
    ):
        claim_connection:Connection = self.__provisioning.claim_client.connect_to(self.__endpoint)
        subscribed_topic_names:List[str] = self.__provisioning.subscribe_all_topics(claim_connection)
        result = self.check_communication_between(
            publisher = self.__provisioning.register_thing_by(claim_connection, name=publisher_name),
            subscriber = self.__provisioning.register_thing_by(claim_connection, name=subscriber_name),
        )
        self.__provisioning.unsubscribe_all_topics_and_disconnect(
            claim_connection,
            subscribed_topic_names
        )
        return result


    def check_communication_between(self, publisher:Client, subscriber:Client):
        result = self.__callback.excute_callback_on(
            client = subscriber,
            callback = self.__callback.subscribe,
            publisher = publisher,
        )
        return result