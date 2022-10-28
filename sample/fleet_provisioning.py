from multiprocessing.connection import Client
from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.account import Endpoint, get_endpoint_of
from src.fleet_provisioning.util import get_current_time

thing_name_key:str = 'device_id'
isengard_virginia:Endpoint = get_endpoint_of(account_name='isengard')
fp:Endpoint = isengard_virginia.set_FP(template_name='aws-iot')

def provision_thing():
    template_parameters:dict = {
        thing_name_key: get_current_time()
    }
    provisioned_thing = fp.provision_thing(
        template_parameters = template_parameters,
        name = template_parameters.get(thing_name_key)
    )
    return provisioned_thing


isengard_virginia.check_communication_between(
    publisher = provision_thing(),
    subscriber = provision_thing(),
)