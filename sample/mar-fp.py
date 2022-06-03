from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Endpoint, get_endpoint_of

def check_fp_on(account_name:str) -> None:
    virginia:Endpoint = get_endpoint_of(account_name, region='us-east-1')
    fp_virginia:Endpoint = virginia.set_FP('ec2')

    publisher_name:str = f'{account_name}_publisher'
    subscriber_name:str = f'{account_name}_subscriber'

    publisher = fp_virginia.provision_thing(
        name = publisher_name,
        template_parameters = {'DeviceID': publisher_name},
    )
    subscriber = fp_virginia.provision_thing(
        name = subscriber_name,
        template_parameters = {'DeviceID': subscriber_name},
    )

    fp_virginia.check_communication_between(publisher, subscriber)



check_fp_on(account_name='test')
check_fp_on(account_name='multi')