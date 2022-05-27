# from broker import Broker
# from pubsub.pubsub import Client
# from awscrt import mqtt


# def connect(env_name:str, region:str, project_name:str) -> None:
#     from threading import Event
#     received_event:Event = Event()

#     def on_message_received(topic:str, payload:dict, dup, qos, retain, **kwargs) -> None:
#         print(f"Received {payload} from {topic}")
#         received_event.set()

#     broker:Broker = Broker(env_name, region)
#     client:Client = broker.connect_for(project_name)
#     client.subscribe(callback=on_message_received, QoS=mqtt.QoS.AT_LEAST_ONCE)
#     client.publish(payload={'project name': project_name}, QoS=mqtt.QoS.AT_LEAST_ONCE)
#     print("Waiting for all messages to be received...")
#     received_event.wait()
#     client.disconnect()


# if __name__ == '__main__':
#     connect(
#         env_name = 'test',
#         region = 'us-east-1',
#         project_name = 'test',
#     )




from account import Account
from broker import Broker
from project import Project
from client import Client
from connection import Connection
from topic import Topic

from fleetprovisioning import FleetProvisionning


def provision_thing(self, fp_project:Project) -> Client:
    claim:Client = self.create_client_using(certs_dir='claim')
    provisioning_connection:Connection = claim.connect()
    
    thing_name:str = response.thing_name
    individual:Client = self.create_client_using(certs_dir=f'individual/{thing_name}')
    return individual


test:Account = Account(name='test')
burner:Account = Account(name='burner')

virginia:Broker = test.use(region='us-east-1')
tokyo:Broker = test.use(region='ap-northeast-1')

fp:Project = virginia.create_project(name='fleet_provisioning')
client1:Client = fp.provision_thing(name='client1')

client1_connection:Connection = client1.connect()
response:dict = client1_connection.disconnect()




topic_aaa:Topic = provisioning_connection.use_topic(name='aaa')
topic_bbb:Topic = provisioning_connection.use_topic(name='bbb')

response:dict = topic_aaa.pub(message)
response:dict = topic_aaa.sub(callback)
response:dict = topic_aaa.unsub()

response:dict = provisioning_connection.disconnect()