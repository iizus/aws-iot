from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Endpoint, get_endpoint_of
test_virginia:Endpoint = get_endpoint_of(account_name='test')

test_virginia.check_communication_on(
    project_name = 'test',
    publisher_name = 'client1',
    subscriber_name = 'client2',
)