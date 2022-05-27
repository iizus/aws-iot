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

test:Account = Account('test')
burner:Account = Account('burner')

virginia:Broker = test.use(region='us-east-1')
tokyo:Broker = test.use(region='ap-northeast-1')

fp:Project = virginia.create(project_name='fleet_provisioning')
claim:Client = fp.create_client_using(certs_dir='claim')

provisioning_connection:Connection = claim.connect()

topic_aaa:Topic = provisioning_connection.use_topic(name='aaa')
topic_bbb:Topic = provisioning_connection.use_topic(name='bbb')

response:dict = topic_aaa.pub(message)
response:dict = topic_aaa.sub(callback)
response:dict = topic_aaa.unsub()

response:dict = provisioning_connection.disconnect()

individual:Client = fp.create_client_using(certs_dir='individual')
individual_connection:Connection = individual.connect()
response:dict = individual_connection.disconnect()