from threading import Event
from awscrt.http import HttpProxyOptions
from src.client.client import Project, Client
from src.client.connection import Topic



class Endpoint:
    from awscrt import mqtt
    from src.client.certs import get_ca_path
    ca_path:str = get_ca_path()

    def __init__(self, name:str) -> None:
        self.name:str = name
        self.ca:str = self.ca_path
        self.port:int = 8883
        self.proxy:HttpProxyOptions = None
        print(f"[Endpoint] Set to {self.name}:{self.port}")


    def set_port(self, number:int=8883):
        return Port(self.name, self.ca, number)


    def check_communication_between(self, publisher:Client, subscriber:Client) -> None:
        subscriber_connection = subscriber.connect_to(self)
        publisher_connection = publisher.connect_to(self)

        topic:str = 'check/communication'
        subscriber_topic = subscriber_connection.use_topic(topic)
        publisher_topic = publisher_connection.use_topic(topic)

        self.__received_event:Event = Event()
        subscriber_topic.subscribe(callback=self.__on_message_received)
        publisher_topic.publish()
        print(f"[{subscriber_connection.client_id}] Waiting... for all messages to be received")
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

        

from src.utils.util import load_json

class Account:
    def __init__(self, name:str='test', config_path:str='endpoint.json') -> None:
        endpoints:dict = load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        print(f"[Account] Set to {name}")


    def get_endpoint_of(self, region:str='us-east-1') -> Endpoint:
        name:str = f'{self.__endpoint_prefix}-ats.iot.{region}.amazonaws.com'
        return Endpoint(name)



class Port(Endpoint):
    def __init__(self, name:str, ca:str, number:int=8883) -> None:
        self.name:str = name
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = None
        print(f"[Endpoint] Set to {self.name}:{self.port}")


    def set_proxy(self, host:str, port:int=443):
        proxy:HttpProxyOptions = HttpProxyOptions(host, port)
        print(f"[Endpoint ]Set HTTP proxy as {host}:{port} for {self.name}:{self.port}")
        return Proxy(self.name, self.ca, self.port, proxy)



class Proxy(Port):
    def __init__(self, name:str, ca:str, number:int=8883, proxy:HttpProxyOptions=None) -> None:
        self.name:str = name
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = proxy



def get_endpoint_of(account_name:str='test', region:str='us-east-1') -> Endpoint:
    env:Account = Account(account_name)
    endpoint:Endpoint = env.get_endpoint_of(region)
    return endpoint


def check_fp_on(account_name:str) -> None:
    fp_virginia:Endpoint = get_endpoint_of(account_name)
    fp_publisher:Client = fp_virginia.provision_thing(name=f'{account_name}_publisher')
    fp_subscriber:Client = fp_virginia.provision_thing(name=f'{account_name}_subscriber')
    fp_virginia.check_communication_between(publisher=fp_publisher, subscriber=fp_subscriber)