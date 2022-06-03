from src.fleet_provisioning.fp import FP

class FleetProvisioning:
    from uuid import uuid4
    from awscrt.mqtt import Connection

    def __init__(self, template_name:str) -> None:
        self.__template_name:str = template_name


    def provision_thing(
        self,
        connection:Connection,
        template_parameters:str,
        thing_name:str = str(uuid4()),
    ) -> str:
        fp:FP = FP(self.__template_name)
        provisioned_thing_name:str = fp.provision_thing(connection, template_parameters, thing_name)
        return provisioned_thing_name