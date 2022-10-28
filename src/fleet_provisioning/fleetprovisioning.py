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
        return provisioned_thing_name