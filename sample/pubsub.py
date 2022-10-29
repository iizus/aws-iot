from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.topic import Topic
from src.client.client import Client
from src.client.connection import Connection
from src.client.account import Endpoint, get_endpoint_of


isengard_virginia:Endpoint = get_endpoint_of(account_name='isengard')
fp:Endpoint = isengard_virginia.set_FP(
    template_name = 'aws-iot',
    thing_name_key = 'device_id'
)

client:Client = fp.provision_thing()
connection:Connection = client.connect_to(endpoint=isengard_virginia)
topic:Topic = connection.use_topic('check/communication')
topic.publish(message={'from': client.id})