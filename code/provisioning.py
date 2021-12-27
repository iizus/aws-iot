from mqtt import MQTT, get_config
from fleetprovisioning import FleetProvisioning
from awscrt.mqtt import Connection


class Provisioning:
    def __init__(self, endpoint:str, template_name:str) -> None:
        self.__mqtt:MQTT = MQTT(endpoint)
        self.__fleet_provisioning:FleetProvisioning = FleetProvisioning(template_name)

    def provision_thing_by(
        self,
        cert:str,
        key:str,
        ca:str,
        client_id:str,
        template_parameters:str,
    ) -> str:
        connection:Connection = self.__mqtt.connect_with(cert, key, ca, client_id)
        thing_name:str = self.__fleet_provisioning.provision_thing_by(
            connection,
            template_parameters
        )
        self.__mqtt.disconnect(connection)
        return thing_name



if __name__ == '__main__':
    config:dict = get_config(file_path='config.json')

    provisioning = Provisioning(
        endpoint = config.get('endpoint'),
        template_name = config.get('template_name')
    )

    from uuid import uuid4
    folder:str = 'certs'
    claim:str = f'{folder}/claim.pem'
    device_ID:str = str(uuid4())
    print(f"Device ID: {device_ID}")

    thing_name:str = provisioning.provision_thing_by(
        cert = f'{claim}.crt',
        key = f'{claim}.key',
        ca = f'{folder}/AmazonRootCA1.pem',
        client_id = device_ID,
        template_parameters = {"DeviceID": device_ID},
    )