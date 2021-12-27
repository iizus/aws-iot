from client import Client
from fleetprovisioning import FleetProvisioning
from awscrt.mqtt import Connection


class Provisioning:
    def __init__(self, endpoint:str, ca:str, template_name:str) -> None:
        self.__client:Client = Client(endpoint, ca)
        self.__fleet_provisioning:FleetProvisioning = FleetProvisioning(template_name)

    def provision_thing_by(
        self,
        cert:str,
        key:str,
        client_id:str,
        template_parameters:str,
    ) -> str:
        connection:Connection = self.__client.connect(cert, key, client_id)
        thing_name:str = self.__fleet_provisioning.provision_thing_by(
            connection,
            template_parameters,
        )
        self.__client.disconnect()
        return thing_name


if __name__ == '__main__':
    from client import read_config
    config:dict = read_config(file_path='config.json')
    folder:str = 'certs'

    provisioning = Provisioning(
        endpoint = config.get('endpoint'),
        ca = f'{folder}/AmazonRootCA1.pem',
        template_name = config.get('template_name'),
    )

    from uuid import uuid4
    claim_cert:str = f'{folder}/claim.pem'
    device_ID:str = str(uuid4())
    print(f"Device ID: {device_ID}")

    thing_name:str = provisioning.provision_thing_by(
        cert = f'{claim_cert}.crt',
        key = f'{claim_cert}.key',
        client_id = device_ID,
        template_parameters = {"DeviceID": device_ID},
    )