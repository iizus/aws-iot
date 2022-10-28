from multiprocessing.connection import Client
from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


import datetime
from src.client.account import Endpoint, get_endpoint_of
from src.client.client import Project

def get_current_time(timezone: datetime.timezone) -> str:
    now = datetime.datetime.now(tz=timezone)
    thing_name:str = now.strftime('%Y-%m-%dT%H-%M-%S')
    return thing_name


test_virginia:Endpoint = get_endpoint_of(account_name='isengard')
fp:Endpoint = test_virginia.set_FP(template_name='aws-iot')

thing_name_key:str = 'device_id'
nine_hours:datetime.timedelta = datetime.timedelta(hours=9)
JST:datetime.timezone = datetime.timezone(nine_hours)

template_parameters:dict = {
    thing_name_key: get_current_time(timezone=JST)
}
provisioned_thing = fp.provision_thing(
    template_parameters = template_parameters,
    name = template_parameters.get(thing_name_key)
)

aws_iot:Project = Project(name='isengard')
test_virginia.check_communication_between(
    publisher = aws_iot.create_client(client_id='client1'),
    subscriber = provisioned_thing,
)