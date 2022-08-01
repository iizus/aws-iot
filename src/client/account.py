from uuid import uuid4
from threading import Event
from awscrt.http import HttpProxyOptions
from src.utils import util
from src.client.client import Project, Client
from src.client.connection import Topic, Connection
from src.client.certs import get_ca_path

class Endpoint:
    from awscrt import mqtt

    def __init__(self, name:str, ca:str='RSA2048', port:int=8883, proxy:HttpProxyOptions=None, provisioning=None) -> None:
        self.name:str = name
        self.ca:str = ca
        self.ca_path:str = get_ca_path(type=ca)
        self.port:int = port
        self.proxy:HttpProxyOptions = proxy
        self.endpoint:str = f"{self.name}:{self.port}"
        self.__provisioning:Provisioning = provisioning
        fp_template_name:str = 'None' if provisioning is None else provisioning.template_name
        util.print_log(subject='Endpoint', verb='Set', message=f"to {self.endpoint}, CA path: {self.ca_path}, FP template: {fp_template_name}")


    def set_ca(self, type:str='RSA2048'):
        return Endpoint(name=self.name, ca=type, port=self.port, proxy=self.proxy, provisioning=self.__provisioning)


    def set_port(self, number:int=8883):
        return Endpoint(name=self.name, ca=self.ca, port=number, proxy=self.proxy, provisioning=self.__provisioning)

    def set_proxy(self, host:str, port:int):
        options:HttpProxyOptions = HttpProxyOptions(host_name=host, port=port)
        return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=options, provisioning=self.__provisioning)

    # def set_proxy(self, options:HttpProxyOptions=None):
        # return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=options, provisioning=self.__provisioning)


    def set_FP(self, template_name:str):
        provisioning:Provisioning = Provisioning(endpoint=self, template_name=template_name)
        return Endpoint(name=self.name, ca=self.ca, port = self.port, proxy=self.proxy, provisioning=provisioning)


    def provision_thing(self, template_parameters:dict, name:str=str(uuid4())) -> Client:
        util.print_log(subject=name, verb='Provisioning...')
        provisioned_thing:Client = self.__provisioning.provision_thing(template_parameters, name)
        util.print_log(subject=name, verb='Provisioned')
        return provisioned_thing


    def check_communication_on(self, project_name:str, publisher_name:str, subscriber_name:str) -> None:
        project:Project = Project(project_name)
        self.check_communication_between(
            publisher = project.create_client(publisher_name),
            subscriber = project.create_client(subscriber_name),
        )


    def excute_callback_on(self, client:Client, callback, topic:str='test/test') -> None:
        connection:Connection = client.connect_to(self)
        client_topic:Topic = connection.use_topic(topic)
        callback(client_topic)
        connection.disconnect()


    def check_communication_between(self, publisher:Client, subscriber:Client) -> None:
        subscriber_connection = subscriber.connect_to(self)
        publisher_connection = publisher.connect_to(self)

        topic:str = 'check/communication'
        subscriber_topic = subscriber_connection.use_topic(topic)
        publisher_topic = publisher_connection.use_topic(topic)

        self.__received_event:Event = Event()
        subscriber_topic.subscribe(callback=self.__on_message_received)
        publisher_topic.publish({'from': publisher_topic.client_id})
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



from src.fleet_provisioning.fleetprovisioning import FleetProvisioning

class Provisioning:
    def __init__(self, endpoint:Endpoint, template_name:str) -> None:
        self.template_name:str = template_name
        self.__endpoint:Endpoint = endpoint
        self.__fp:FleetProvisioning = FleetProvisioning(template_name)
        self.__project:Project = Project(name='fleet_provisioning')
        self.__claim:Client = self.__project.create_client(client_id='claim')


    def provision_thing(self, template_parameters:dict, name:str=str(uuid4())) -> Client:
        connection:Connection = self.__claim.connect_to(self.__endpoint)
        provisioned_thing_name:str = connection.provision_thing_by(self.__fp, template_parameters, name)
        provisioned_thing:Client = self.__project.create_client(
            client_id = provisioned_thing_name,
            cert_dir = 'individual/'
        )
        return provisioned_thing