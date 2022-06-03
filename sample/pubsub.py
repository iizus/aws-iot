from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Endpoint, get_endpoint_of
from src.client.client import Project

test_virginia:Endpoint = get_endpoint_of(account_name='test')
test:Project = Project(name='test')

test_virginia.check_communication_between(
    publisher = test.create_client(client_id='client1'),
    subscriber = test.create_client(client_id='client2')
)