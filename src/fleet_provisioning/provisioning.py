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
        self.template_name:str = template_name
        self.__endpoint:Endpoint = endpoint
        self.__fp:FleetProvisioning = FleetProvisioning(template_name, thing_name_key)
        self.__project:Project = Project(name='fleet_provisioning')
        self.claim_client:Client = self.__project.create_client(client_id='claim')


    def provision_thing(self, name:str=get_current_time()) -> Client:
        util.print_log(subject=name, verb='Provisioning...')
        claim_connection:Connection = self.claim_client.connect_to(self.__endpoint)
        provisioned_thing:Client = self.__project.create_client(
            client_id = self.__fp.provision_thing(claim_connection, name),
            cert_dir = 'individual/'
        )
        util.print_log(subject=name, verb='Provisioned')
        return provisioned_thing


    def register_thing_by(
        self,
        claim_connection:Connection,
        name:str = get_current_time(),
    ) -> Client:
        util.print_log(subject=name, verb='Provisioning...')
        provisioned_thing:Client = self.__project.create_client(
            client_id = self.__fp.register_thing_by(claim_connection, name),
            cert_dir = 'individual/'
        )
        util.print_log(subject=name, verb='Provisioned')
        return provisioned_thing


    def subscribe_all_topics(self, claim_connection:Connection) -> List[str]:
        subscribed_topic_names:List[str] = self.__fp.subscribe_all_topics(claim_connection)
        return subscribed_topic_names

    
    def unsubscribe_all_topics_and_disconnect(
        self,
        claim_connection:Connection, 
        subscribed_topic_names:List[str],
    ) -> dict:
        return self.__fp.unsubscribe_all_topics_and_disconnect(
            claim_connection,
            subscribed_topic_names
        )