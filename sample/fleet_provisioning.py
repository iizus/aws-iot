from multiprocessing.connection import Client
from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.account import Endpoint, get_endpoint_of
isengard_virginia:Endpoint = get_endpoint_of(account_name='isengard')
fp:Endpoint = isengard_virginia.set_FP(
    template_name = 'aws-iot',
    thing_name_key = 'device_id'
)

isengard_virginia.check_communication_between(
    publisher = fp.provision_thing(),
    subscriber = fp.provision_thing(),
)