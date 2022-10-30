from awscrt.http import HttpProxyOptions
from src.utils import util
from src.client.client import Client
from src.client.connection import Connection
from src.client.certs import get_ca_path
from src.fleet_provisioning.util import get_current_time

DEFAULT:dict = util.load_json('default.json')

class Endpoint:
    def __init__(
        self,
        name:str,
        ca:str = 'RSA2048',
        port:int = 8883,
        proxy:HttpProxyOptions = None,
    ) -> None:
        self.name:str = name
        self.ca:str = ca
        self.ca_path:str = get_ca_path(type=ca)
        self.port:int = port
        self.proxy:HttpProxyOptions = proxy
        self.endpoint:str = f"{self.name}:{self.port}"

        util.print_log(
            subject = 'Endpoint',
            verb = 'Set',
            message = f"to {self.endpoint}, CA path: {self.ca_path}"
        )

    def set_ca(self, type:str='RSA2048'):
        return Endpoint(name=self.name, ca=type, port=self.port, proxy=self.proxy)

    def set_port(self, number:int=8883):
        return Endpoint(name=self.name, ca=self.ca, port=number, proxy=self.proxy)

    def set_proxy(self, host:str, port:int):
        options:HttpProxyOptions = HttpProxyOptions(host_name=host, port=port)
        return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=options)



from src.client.project import Project
from src.client.account import get_endpoint
from src.fleet_provisioning.fleetprovisioning import FleetProvisioning

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
        self.__claim_client:Client = self.__project.create_client(client_id='claim')


    def provision_thing(self, name:str=get_current_time()) -> Client:
        util.print_log(subject=name, verb='Provisioning...')
        provisioned_thing:Client = self.__provision_thing(name)
        util.print_log(subject=name, verb='Provisioned')
        return provisioned_thing


    def __provision_thing(self, name:str=get_current_time()) -> Client:
        connection:Connection = self.__claim_client.connect_to(self.__endpoint)
        provisioned_thing:Client = self.__project.create_client(
            client_id = connection.provision_thing_by(self.__fp, name),
            cert_dir = 'individual/'
        )
        return provisioned_thing