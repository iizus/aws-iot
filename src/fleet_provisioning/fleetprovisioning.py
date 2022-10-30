# from os import rename
# from src.utils import util
from src.fleet_provisioning.fp import FP
from src.fleet_provisioning import util
from awsiot.iotidentity import IotIdentityClient, CreateKeysAndCertificateResponse


class FleetProvisioning:
    from uuid import uuid4
    from awscrt.mqtt import Connection

    def __init__(self, template_name:str, thing_name_key:str) -> None:
        self.__thing_name_key:str = thing_name_key
        self.__fp:FP = FP(template_name)


    def provision_thing(self, connection:Connection, name:str=str(uuid4())) -> str:
        provisioned_thing_name:str = self.__provision_thing(connection, name)
        # if name != provisioned_thing_name:
        #     path:str = 'certs/fleet_provisioning/individual'
        #     old_path:str = f'{path}/{name}'
        #     new_path:str = f'{path}/{provisioned_thing_name}'
        #     util.remove(new_path)
        #     rename(old_path, new_path)
        return provisioned_thing_name


    def __provision_thing(self, connection:Connection, name:str) -> str:
        provisioned_thing_name:str = self.__provision_by(connection, name)
        # self.__print_log(verb='Success', message=f"fleet provisioning of {provisioned_thing_name}")
        return provisioned_thing_name


    def __provision_by(self, connection:Connection, name:str) -> str:
        try:
            # Subscribe to necessary topics.
            # Note that is **is** important to wait for "accepted/rejected" subscriptions
            # to succeed before publishing the corresponding "request".
            client:IotIdentityClient = IotIdentityClient(connection)
            provisioned_thing_name:str = self.__provision_thing_by(client, name)
            return provisioned_thing_name
        except Exception as e:
            util.error(e)


    def __provision_thing_by(self, client:IotIdentityClient, name:str) -> str:
        provisioned_thing_name:str = self.__fp.register_thing_by(
            client = client,
            template_parameters = { self.__thing_name_key: name },
            cert = self.__fp.get_keys_and_certificate_by(client, name),
        )
        return provisioned_thing_name