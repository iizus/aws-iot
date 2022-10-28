from typing import Literal
from awscrt import mqtt
from src.utils import util
from src.client.topic import Topic
from src.fleet_provisioning.fleetprovisioning import FleetProvisioning



class Connection:
    from uuid import uuid4

    def __init__(self, project_name:str, connection:mqtt.Connection) -> None:
        self.__project_name:str = project_name
        self.__connection:mqtt.Connection = connection
        self.client_id:str = connection.client_id


    def use_topic(
        self,
        name:str = None,
        QoS:Literal = mqtt.QoS.AT_MOST_ONCE,
        retain:bool = False
    ):
        return Topic(self.__project_name, self.__connection, name, QoS, retain)


    def disconnect(self) -> dict:
        client_id:str = self.__connection.client_id
        util.print_log(subject=client_id, verb="Disconnecting...")
        disconnect_result:dict = self.__connection.disconnect().result()
        util.print_log(subject=client_id, verb='Disconnected', message=f"Result: {disconnect_result}")
        return disconnect_result


    def provision_thing_by(self, fp:FleetProvisioning, name:str=str(uuid4())) -> str:
        provisioned_thing_name:str = fp.provision_thing(self.__connection, name)
        self.disconnect()
        return provisioned_thing_name