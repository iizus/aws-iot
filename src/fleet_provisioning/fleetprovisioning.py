# from os import rename
# from src.utils import util
from src.fleet_provisioning.fp import FP_base
from src.fleet_provisioning import util
from awsiot.iotidentity import IotIdentityClient, CreateKeysAndCertificateResponse


class FleetProvisioning:
    from uuid import uuid4
    from awscrt.mqtt import Connection

    def __init__(self, template_name:str, thing_name_key:str) -> None:
        self.__thing_name_key:str = thing_name_key
        # self.__fp:FP = FP(template_name)
        self.__fp:FP_base = FP_base(template_name)


    def provision_thing(self, connection:Connection, name:str=str(uuid4())) -> str:
        template_parameters:dict = { self.__thing_name_key: name }
        provisioned_thing_name:str = self.__provision_thing(
            connection,
            template_parameters,
            name,
        )
        # if name != provisioned_thing_name:
        #     path:str = 'certs/fleet_provisioning/individual'
        #     old_path:str = f'{path}/{name}'
        #     new_path:str = f'{path}/{provisioned_thing_name}'
        #     util.remove(new_path)
        #     rename(old_path, new_path)
        return provisioned_thing_name


    def __provision_thing(
        self,
        connection:Connection,
        template_parameters:dict,
        # thing_name:str = util.get_current_time(),
        name:str,
    ) -> str:
        # self.__thing_name:str = thing_name
        provisioned_thing_name:str = self.__provision_by(connection, template_parameters, name)
        # self.__print_log(verb='Success', message=f"fleet provisioning of {provisioned_thing_name}")
        return provisioned_thing_name


    def __provision_by(self, connection:Connection, template_parameters:dict, name:str) -> str:
        # self.__claim:str = connection.client_id
        try:
            # Subscribe to necessary topics.
            # Note that is **is** important to wait for "accepted/rejected" subscriptions
            # to succeed before publishing the corresponding "request".
            client:IotIdentityClient = IotIdentityClient(connection)
            provisioned_thing_name:str = self.__provision_thing_by(client, template_parameters, name)
            return provisioned_thing_name
        except Exception as e:
            util.error(e)


    def __provision_thing_by(
        self,
        client:IotIdentityClient,
        template_parameters:dict,
        name:str,
    ) -> str:
        # provisioning_thing_name:str = template_parameters.get(self.__thing_name_key)
        cert:CreateKeysAndCertificateResponse = self.__fp.get_keys_and_certificate_by(client, name)
        provisioned_thing_name:str = self.__fp.register_thing_by(client, template_parameters, cert)
        return provisioned_thing_name