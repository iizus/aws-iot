from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Endpoint, get_endpoint_of
from src.client.client import Project

test_virginia:Endpoint = get_endpoint_of(account_name='isengard')
fp:Endpoint = test_virginia.set_FP(template_name='aws-iot')

aws_iot:Project = Project(name='isengard')
# provisioning_thing_name:str = 'fddddfd'

import datetime
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
provisioning_thing_name:str = now.strftime('%Y-%m-%dT%H-%M-%S')

template_parameters:dict = {'device_id': provisioning_thing_name}

test_virginia.check_communication_between(
    publisher = aws_iot.create_client(client_id='client1'),
    subscriber = fp.provision_thing(template_parameters, provisioning_thing_name),
)