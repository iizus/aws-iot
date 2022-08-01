from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Endpoint, get_endpoint_of
test_virginia:Endpoint = get_endpoint_of(account_name='test', region='us-east-1')
test_virginia.set_proxy(options=None)

from src.client.client import Client, Project
project:Project = Project('test')
client_id:str = 'client1'
client:Client = project.create_client(client_id)

from src.client.connection import Connection
connection:Connection = client.connect_to(endpoint=test_virginia)

from src.client.topic import Topic
topic:Topic = connection.use_topic('check/communication')
topic.publish(message={'from': client_id})