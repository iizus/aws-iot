# from os import rename
# from src.utils import util
from src.fleet_provisioning.fp import FP


class FleetProvisioning:
    from uuid import uuid4
    from awscrt.mqtt import Connection

    def __init__(self, template_name:str, thing_name_key:str) -> None:
        self.__template_name:str = template_name
        self.__thing_name_key = thing_name_key


    def provision_thing(
        self,
        connection:Connection,
        name:str = str(uuid4()),
    ):
        fp:FP = FP(self.__template_name)
        template_parameters:dict = { self.__thing_name_key: name }
        provisioned_thing_name:str = fp.provision_thing(
            connection,
            template_parameters,
            name
        )
        # if name != provisioned_thing_name:
        #     path:str = 'certs/fleet_provisioning/individual'
        #     old_path:str = f'{path}/{name}'
        #     new_path:str = f'{path}/{provisioned_thing_name}'
        #     util.remove(new_path)
        #     rename(old_path, new_path)
        return provisioned_thing_name