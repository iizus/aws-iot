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
        connection:Connection = self.claim_client.connect_to(self.__endpoint)
        provisioned_thing:Client = self.provision_thing_by(connection, name)
        connection.disconnect()
        return provisioned_thing


    def provision_thing_by(
        self,
        connection:Connection,
        name:str = get_current_time(),
    ) -> Client:
        util.print_log(subject=name, verb='Provisioning...')
        provisioned_thing:Client = self.__project.create_client(
            client_id = self.__fp.provision_thing(connection, name),
            cert_dir = 'individual/'
        )
        util.print_log(subject=name, verb='Provisioned')
        return provisioned_thing