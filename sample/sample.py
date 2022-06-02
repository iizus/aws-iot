from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from src.client.account import Account, Endpoint
from src.client.client import Project, Client



test_env:Account = Account(name='test')
burner_env:Account = Account(name='burner')

test_virginia:Endpoint = test_env.get_endpoint_of(region='us-east-1')
test_tokyo:Endpoint = test_env.get_endpoint_of(region='ap-northeast-1')

test_virginia_443:Endpoint = test_virginia.set_port(443)
test_virginia_443_ca:Endpoint = test_virginia_443.set_ca(type='RSA2048')

test:Project = Project(name='test')

test_subscriber:Client = test.create_client(client_id='client1')
test_publisher:Client = test.create_client(client_id='client2')

test_virginia_443.check_communication_between(publisher=test_publisher, subscriber=test_subscriber)