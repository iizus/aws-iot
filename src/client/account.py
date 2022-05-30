from awscrt.http import HttpProxyOptions

class Proxy:
    def __init__(self, name:str, ca:str, number:int=8883, proxy:HttpProxyOptions=None) -> None:
        self.name:str = name
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = proxy



class Port:
    def __init__(self, name:str, ca:str, number:int=8883) -> None:
        self.name:str = name
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = None
        print(f"[Endpoint] Set to {self.name}:{self.port}")


    def set_proxy(self, host:str, port:int=443) -> Proxy:
        proxy:HttpProxyOptions = HttpProxyOptions(host, port)
        print(f"[Endpoint ]Set HTTP proxy as {host}:{port} for {self.name}:{self.port}")
        return Proxy(self.name, self.ca, self.port, proxy)



from src.client.client import Project, Client
from time import sleep

class Endpoint:
    from src.client.certs import get_ca_path
    ca_path:str = get_ca_path()

    def __init__(self, name:str) -> None:
        self.name:str = name
        self.ca:str = self.ca_path
        self.port:int = 8883
        self.proxy:HttpProxyOptions = None
        print(f"[Endpoint] Set to {self.name}:{self.port}")


    def set_port(self, number:int=8883) -> Port:
        return Port(self.name, self.ca, number)


    def check_communication_between(self, publisher:Client, subscriber:Client) -> None:
        subscriber_connection = subscriber.connect_to(self)
        publisher_connection = publisher.connect_to(self)

        topic:str = 'test/test'
        subscriber_topic = subscriber_connection.use_topic(topic)
        publisher_topic = publisher_connection.use_topic(topic)

        subscriber_topic.subscribe()
        publisher_topic.publish()
        sleep(2)
        subscriber_topic.unsubscribe()
        sleep(2)
        subscriber_connection.disconnect()
        publisher_connection.disconnect()


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