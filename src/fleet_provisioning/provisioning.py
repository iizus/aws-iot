from typing import List
from src.utils import util
from src.client.client import Client
from src.client.connection import Connection
from src.fleet_provisioning.util import get_current_time
from src.client.project import Project
from src.client.account import get_endpoint, Endpoint
from src.fleet_provisioning.fleetprovisioning import FleetProvisioning


DEFAULT:dict = util.load_json('default.json')


class Provisioning:
    def __init__(
        self,
        endpoint:Endpoint = get_endpoint(),
        template_name:str = DEFAULT.get('TEMPLATE_NAME'),
        thing_name_key:str = DEFAULT.get('THING_NAME_KEY'),
    ) -> None:
        self.__project:Project = Project(name='fleet_provisioning')
        self.__claim_client:Client = self.__project.create_client(client_id='claim')
        claim_connection:Connection = self.__claim_client.connect_to(endpoint)
        self.__subscribed_topic_names:List[str] = list()
        self.__fp:FleetProvisioning = FleetProvisioning(template_name, thing_name_key, claim_connection)


    def provision_thing(self, name:str=get_current_time()) -> Client:
        self.subscribe_all_topics()
        provisioned_thing:str = self.register_thing_as(name)
        self.unsubscribe_all_topics_and_disconnect()
        return provisioned_thing


    def subscribe_all_topics(self) -> List[str]:
        self.__subscribed_topic_names += self.__fp.subscribe_CreateKeysAndCertificate_topics()
        self.__subscribed_topic_names += self.__fp.subscribe_RegisterThing_topics()
        return self.__subscribed_topic_names


    def register_thing_as(self, name:str = get_current_time()) -> Client:
        util.print_log(subject=name, verb='Provisioning...')
        provisioned_thing:Client = self.__project.create_client(
            client_id = self.__fp.register_thing_by(name),
            cert_dir = 'individual/'
        )
        util.print_log(subject=name, verb='Provisioned successfully')
        return provisioned_thing

    
    def unsubscribe_all_topics_and_disconnect(self) -> dict:
        return self.__fp.unsubscribe_all_topics_and_disconnect(self.__subscribed_topic_names)