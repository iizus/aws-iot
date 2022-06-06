from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Endpoint, get_endpoint_of
from src.client.client import Project

test_virginia:Endpoint = get_endpoint_of(account_name='test')
fp:Endpoint = test_virginia.set_FP(template_name='simple')

test:Project = Project(name='test')
provisioning_thing_name:str = 'before_provisioned_thing'
template_parameters:dict = {'DeviceID': provisioning_thing_name}

test_virginia.check_communication_between(
    publisher = test.create_client(client_id='client1'),
    subscriber = fp.provision_thing(template_parameters, provisioning_thing_name),
)