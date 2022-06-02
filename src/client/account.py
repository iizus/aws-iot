from threading import Event
from awscrt.http import HttpProxyOptions
from src.utils import util
from src.client.client import Project, Client
from src.client.connection import Topic, Connection
from src.client.certs import get_ca_path
from src.fleet_provisioning.fleetprovisioning import FleetProvisioning

class Endpoint:
    from awscrt import mqtt
    from uuid import uuid4

    def __init__(self, name:str, ca:str='RSA2048', port:int=8883, proxy:HttpProxyOptions=None, fp:FleetProvisioning=None, claim:Client=None) -> None:
        self.name:str = name
        self.ca:str = ca
        self.ca_path:str = get_ca_path(type=ca)
        self.port:int = port
        self.proxy:HttpProxyOptions = proxy
        self.__fp:FleetProvisioning = fp
        self.__fp_Project:Project = Project(name='fleet_provisioning')
        self.__fp_claim:Client = claim
        self.endpoint:str = f"{self.name}:{self.port}"
        util.print_log(subject='Endpoint', verb='Set', message=f"to {self.endpoint}, CA path: {self.ca_path}, FP: {fp}")


    def set_ca(self, type:str='RSA2048'):
        return Endpoint(name=self.name, ca=type, port=self.port, proxy=self.proxy, fp=self.__fp, claim=self.__fp_claim)


    def set_port(self, number:int=8883):
        return Endpoint(name=self.name, ca=self.ca, port=number, proxy=self.proxy, fp=self.__fp, claim=self.__fp_claim)


    def set_proxy(self, options:HttpProxyOptions=None):
        return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=options, fp=self.__fp, claim=self.__fp_claim)


    def set_FP(self, template_name:str):
        self.__fp:FleetProvisioning = FleetProvisioning(template_name)
        self.__fp_claim:Client = self.__fp_Project.create_client(client_id='claim')
        return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=self.proxy, fp=self.__fp, claim=self.__fp_claim)


    def provision_thing(self, name:str=str(uuid4())) -> Client:
        provisioning_connection:Connection = self.__fp_claim.connect_to(self)
        thing_name:str = provisioning_connection.provision_thing_by(self.__fp, name)
        fp_thing:Client = self.__fp_Project.create_client(client_id=thing_name, cert_dir='individual/')
        return fp_thing


    def check_communication_between(self, publisher:Client, subscriber:Client) -> None:
        subscriber_connection = subscriber.connect_to(self)
        publisher_connection = publisher.connect_to(self)

        topic:str = 'check/communication'
        subscriber_topic = subscriber_connection.use_topic(topic)
        publisher_topic = publisher_connection.use_topic(topic)

        self.__received_event:Event = Event()
        subscriber_topic.subscribe(callback=self.__on_message_received)
        publisher_topic.publish()
        client_id:str = subscriber_connection.client_id
        util.print_log(subject=client_id, verb='Waiting...', message="for all messages to be received")
        self.__received_event.wait()
        subscriber_topic.unsubscribe()

        subscriber_connection.disconnect()
        publisher_connection.disconnect()


    def __on_message_received(self, topic:str, payload:str, dup:bool, qos:mqtt.QoS, retain:bool, **kwargs:dict) -> None:
        Topic.print_recieved_message(topic, payload, dup, qos, retain, **kwargs)
        self.__received_event.set()



import awsiot
print(f"Version of AWS IoT Device SDK for Python v2: {awsiot.__version__}")

class Account:
    def __init__(self, name:str='test', config_path:str='endpoint.json') -> None:
        endpoints:dict = util.load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        util.print_log(subject='Account', verb='Set', message=f"to {name}")


    def get_endpoint_of(self, region:str='us-east-1') -> Endpoint:
        name:str = f'{self.__endpoint_prefix}-ats.iot.{region}.amazonaws.com'
        return Endpoint(name)



def get_endpoint_of(account_name:str='test', region:str='us-east-1') -> Endpoint:
    env:Account = Account(account_name)
    endpoint:Endpoint = env.get_endpoint_of(region)
    return endpoint


def check_fp_on(account_name:str, template_name:str) -> None:
    virginia:Endpoint = get_endpoint_of(account_name, region='us-east-1')
    fp_virginia:Endpoint = virginia.set_FP(template_name)
    fp_virginia.check_communication_between(
        publisher = fp_virginia.provision_thing(name=f'{account_name}_publisher'),
        subscriber = fp_virginia.provision_thing(name=f'{account_name}_subscriber')
    )