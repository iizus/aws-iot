# from os import rename
# from src.utils import util

from src.fleet_provisioning.fp import FP
from src.fleet_provisioning.util import get_current_time, error
from awsiot.iotidentity import IotIdentityClient


class FleetProvisioning:
    from awscrt.mqtt import Connection

    def __init__(self, template_name:str, thing_name_key:str) -> None:
        self.__thing_name_key:str = thing_name_key
        self.__fp:FP = FP(template_name)


    def provision_thing(self, connection:Connection, name:str=get_current_time()) -> str:
        try:
            # Subscribe to necessary topics.
            # Note that is **is** important to wait for "accepted/rejected" subscriptions
            # to succeed before publishing the corresponding "request".
            provisioned_thing_name:str = self.__provision_thing_by(connection, name)
            # self.__print_log(verb='Success', message=f"fleet provisioning of {provisioned_thing_name}")
            return provisioned_thing_name
        except Exception as e:
            error(e)
        
        # if name != provisioned_thing_name:
        #     path:str = 'certs/fleet_provisioning/individual'
        #     old_path:str = f'{path}/{name}'
        #     new_path:str = f'{path}/{provisioned_thing_name}'
        #     util.remove(new_path)
        #     rename(old_path, new_path)
        return provisioned_thing_name


    def __provision_thing_by(
        self,
        connection:Connection,
        name:str = get_current_time()
    ) -> str:
        claim:IotIdentityClient = IotIdentityClient(connection)
        provisioned_thing_name:str = self.__fp.register_thing_by(
            client = claim,
            template_parameters = { self.__thing_name_key: name },
            provisioning_thing_name = name,
        )
        return provisioned_thing_name