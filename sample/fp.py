from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from src.client.account import Account, Endpoint
from src.client.client import Project, Client
from time import sleep



test_env:Account = Account(name='test')
test_virginia:Endpoint = test_env.get_endpoint_of(region='us-east-1')

test:Project = Project(name='test')
test_subscriber:Client = test.create_client(client_id='client1')
test_publisher:Client = test_virginia.provision_thing(name='publisher')

test_subscriber_connection = test_subscriber.connect_to(test_virginia)
test_publisher_connection = test_publisher.connect_to(test_virginia)

topic:str = 'test/test'
subscriber_topic_test = test_subscriber_connection.use_topic(topic)
publisher_topic_test = test_publisher_connection.use_topic(topic)

subscriber_topic_test.subscribe()
publisher_topic_test.publish()
sleep(2)
subscriber_topic_test.unsubscribe()
sleep(2)
test_subscriber_connection.disconnect()
test_publisher_connection.disconnect()