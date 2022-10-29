from threading import Event
from awscrt.http import HttpProxyOptions
from src.utils import util
from src.client.client import Client
from src.client.connection import Topic, Connection
from src.client.certs import get_ca_path
from src.fleet_provisioning.util import get_current_time

DEFAULT_TOPIC:str = 'check/communication'


class Endpoint:
    from awscrt import mqtt

    def __init__(
        self,
        name:str,
        ca:str = 'RSA2048',
        port:int = 8883,
        proxy:HttpProxyOptions = None,
        provisioning = None
    ) -> None:
        self.name:str = name
        self.ca:str = ca
        self.ca_path:str = get_ca_path(type=ca)
        self.port:int = port
        self.proxy:HttpProxyOptions = proxy
        self.endpoint:str = f"{self.name}:{self.port}"
        self.__provisioning:Provisioning = provisioning
        fp_template_name:str = 'None' if provisioning is None else provisioning.template_name
        
        util.print_log(
            subject = 'Endpoint',
            verb = 'Set',
            message = f"to {self.endpoint}, CA path: {self.ca_path}, FP template: {fp_template_name}"
        )


    def set_ca(self, type:str='RSA2048'):
        return Endpoint(
            name = self.name,
            ca = type,
            port = self.port,
            proxy = self.proxy,
            provisioning = self.__provisioning
        )

    def set_port(self, number:int=8883):
        return Endpoint(
            name = self.name,
            ca = self.ca,
            port = number,
            proxy = self.proxy,
            provisioning = self.__provisioning
        )

    def set_proxy(self, host:str, port:int):
        options:HttpProxyOptions = HttpProxyOptions(host_name=host, port=port)
        return Endpoint(
            name = self.name,
            ca = self.ca,
            port = self.port,
            proxy = options,
            provisioning = self.__provisioning
        )

    # def set_proxy(self, options:HttpProxyOptions=None):
    #     return Endpoint(
    #          name = self.name,
    #          ca = self.ca,
    #          port = self.port,
    #          proxy = options,
    #          provisioning = self.__provisioning
    #         )

    def set_FP(
        self,
        template_name:str = 'aws-iot',
        thing_name_key:str = 'device_id'
    ):
        provisioning:Provisioning = Provisioning(
            endpoint = self,
            template_name = template_name,
            thing_name_key = thing_name_key,
        )
        return Endpoint(
            name = self.name,
            ca = self.ca,
            port = self.port,
            proxy = self.proxy,
            provisioning = provisioning
        )


    def provision_thing(self) -> Client:
        name:str = get_current_time()
        util.print_log(subject=name, verb='Provisioning...')
        provisioned_thing:Client = self.__provisioning.provision_thing(name)
        util.print_log(subject=name, verb='Provisioned')
        return provisioned_thing


    def check_communication(
        self,
        template_name:str = 'aws-iot',
        thing_name_key:str = 'device_id'
    ) -> None:
        fp:Endpoint = self.set_FP(template_name, thing_name_key)
        self.check_communication_between(
            # publisher = fp.provision_thing(),
            subscriber = fp.provision_thing(),
        )


    def check_communication_between(
        self,
        # publisher:Client,
        subscriber:Client,
        topic:str = DEFAULT_TOPIC
    ) -> None:
        subscriber_connection = subscriber.connect_to(self)
        # publisher_connection = publisher.connect_to(self)

        subscriber_topic = subscriber_connection.use_topic(topic)
        # publisher_topic = publisher_connection.use_topic(topic)

        self.__received_event:Event = Event()
        subscriber_topic.subscribe(callback=self.__on_message_received)

        # publisher_topic.publish({'from': publisher_topic.client_id})
        self.check_publishing()
        
        client_id:str = subscriber_connection.client_id
        util.print_log(
            subject = client_id,
            verb = 'Waiting...',
            message = "for all messages to be received"
        )
        self.__received_event.wait()
        subscriber_topic.unsubscribe()

        subscriber_connection.disconnect()
        # publisher_connection.disconnect()


    def check_publishing(self) -> None:
        fp:Endpoint = self.set_FP()
        self.excute_callback_on(
            client = fp.provision_thing(),
            callback = publish
        )


    def excute_callback_on(self, client:Client, callback, topic:str=DEFAULT_TOPIC) -> None:
        connection:Connection = client.connect_to(self)
        client_topic:Topic = connection.use_topic(topic)
        callback(client_topic)
        connection.disconnect()


    def __on_message_received(
        self,
        topic:str,
        payload:str,
        dup:bool,
        qos:mqtt.QoS,
        retain:bool,
        **kwargs:dict
    ) -> None:
        Topic.print_recieved_message(topic, payload, dup, qos, retain, **kwargs)
        self.__received_event.set()


def publish(topic:Topic) -> None:
    topic.publish({'from': topic.client_id})



from src.client.client import Project
from src.fleet_provisioning.fleetprovisioning import FleetProvisioning

class Provisioning:
    def __init__(self, endpoint:Endpoint, template_name:str, thing_name_key:str) -> None:
        self.template_name:str = template_name
        self.__endpoint:Endpoint = endpoint
        self.__fp:FleetProvisioning = FleetProvisioning(template_name, thing_name_key)
        self.__project:Project = Project(name='fleet_provisioning')
        self.__claim:Client = self.__project.create_client(client_id='claim')


    def provision_thing(self, name:str=get_current_time()) -> Client:
        connection:Connection = self.__claim.connect_to(self.__endpoint)
        provisioned_thing:Client = self.__project.create_client(
            client_id = connection.provision_thing_by(self.__fp, name),
            cert_dir = 'individual/'
        )
        return provisioned_thing