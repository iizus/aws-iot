from threading import Event
from awscrt.http import HttpProxyOptions
from src.utils import util
from src.client.client import Project, Client
from src.client.connection import Topic
from src.client.certs import get_ca_path

class Endpoint:
    from awscrt import mqtt

    def __init__(self, name:str, ca:str='RSA2048', port:int=8883, proxy:HttpProxyOptions=None) -> None:
        self.name:str = name
        self.ca:str = ca
        self.ca_path:str = get_ca_path(type=ca)
        self.port:int = port
        self.proxy:HttpProxyOptions = proxy
        self.endpoint:str = f"{self.name}:{self.port}"
        util.print_log(subject='Endpoint', verb='Set', message=f"to {self.endpoint} and CA path: {self.ca_path}")


    def set_ca(self, type:str='RSA2048'):
        return Endpoint(name=self.name, ca=type, port=self.port, proxy=self.proxy)


    def set_port(self, number:int=8883):
        return Endpoint(name=self.name, ca=self.ca, port=number, proxy=self.proxy)


    def set_proxy(self, options:HttpProxyOptions=None):
        return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=options)


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


    def provision_thing(self, name:str) -> Client:
        fp:Project = Project(name='fleet_provisioning')
        fp_claim:Client = fp.create_client(client_id='claim')
        provisioning_connection = fp_claim.connect_to(self)
        thing_name:str = provisioning_connection.provision_thing(name)
        individual:Client = fp.create_client(client_id=thing_name, cert_dir='individual/')
        return individual

        

class Account:
    def __init__(self, name:str='test', config_path:str='endpoint.json') -> None:
        endpoints:dict = util.load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        print(f"[Account] Set to {name}")


    def get_endpoint_of(self, region:str='us-east-1') -> Endpoint:
        name:str = f'{self.__endpoint_prefix}-ats.iot.{region}.amazonaws.com'
        return Endpoint(name)



def get_endpoint_of(account_name:str='test', region:str='us-east-1') -> Endpoint:
    env:Account = Account(account_name)
    endpoint:Endpoint = env.get_endpoint_of(region)
    return endpoint


def check_fp_on(account_name:str) -> None:
    fp_virginia:Endpoint = get_endpoint_of(account_name, region='us-east-1')
    fp_publisher:Client = fp_virginia.provision_thing(name=f'{account_name}_publisher')
    fp_subscriber:Client = fp_virginia.provision_thing(name=f'{account_name}_subscriber')
    fp_virginia.check_communication_between(publisher=fp_publisher, subscriber=fp_subscriber)