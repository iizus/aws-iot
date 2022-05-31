from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from src.client.account import Account, Endpoint
from src.client.client import Project, Client

from src.client.account import get_endpoint_of

test_virginia:Endpoint = get_endpoint_of(account_name='test')
multi_virginia:Endpoint = get_endpoint_of(account_name='multi')

# test_env:Account = Account(name='test')
# multi_env:Account = Account(name='multi')

# region:str = 'us-east-1'
# test_virginia:Endpoint = test_env.get_endpoint_of(region)
# multi_virginia:Endpoint = multi_env.get_endpoint_of(region)

test:Project = Project(name='test')
test_subscriber:Client = test.create_client(client_id='client1')
test_publisher:Client = test_virginia.provision_thing(name='publisher')

test_virginia.check_communication_between(publisher=test_publisher, subscriber=test_subscriber)