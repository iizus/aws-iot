from src.utils import util
from src.client.account import get_endpoint, Endpoint
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
        self.__callback:PubSub_callback = PubSub_callback(endpoint, topic_name)
        self.provisioning:Provisioning = Provisioning(endpoint, template_name, thing_name_key)


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
        # self.__provisioning.subscribe_all_topics()
        result = self.check_communication_between(
            publisher = self.provisioning.register_thing_as(publisher_name),
            subscriber = self.provisioning.register_thing_as(subscriber_name),
        )
        # self.__provisioning.unsubscribe_all_topics_and_disconnect()
        return result


    def check_communication_between(self, publisher:Client, subscriber:Client):
        result = self.__callback.excute_callback_on(
            client = subscriber,
            callback = self.__callback.subscribe_and_wait_massage,
            publisher = publisher,
        )
        return result