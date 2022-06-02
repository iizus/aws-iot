from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from src.client.account import Account
from src.client.client import Project



test_env:Account = Account(name='test')
burner_env:Account = Account(name='burner')

test_virginia = test_env.get_endpoint_of(region='us-east-1')
test_tokyo = test_env.get_endpoint_of(region='ap-northeast-1')

test_virginia_443 = test_virginia.set_port(443)

test:Project = Project(name='test')

test_subscriber = test.create_client(client_id='client1')
test_publisher = test.create_client(client_id='client2')

test_virginia_443.check_communication_between(publisher=test_publisher, subscriber=test_subscriber)