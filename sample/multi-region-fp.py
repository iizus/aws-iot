from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Account, Endpoint
from src.client.client import Client

def chech_fp_on(region:str):
    test_env:Account = Account(name='test')
    endpoint:Endpoint = test_env.get_endpoint_of(region)
    fp_endpoint:Endpoint = endpoint.set_FP('ec2')

    publisher_name:str = f'{region}_publisher'
    subscriber_name:str = f'{region}_subscriber'

    publisher:Client = fp_endpoint.provision_thing(
        name = publisher_name,
        template_parameters = {'DeviceID': publisher_name},
    )
    subscriber:Client = fp_endpoint.provision_thing(
        name = subscriber_name,
        template_parameters = {'DeviceID': subscriber_name},
    )

    fp_endpoint.check_communication_between(publisher, subscriber)



chech_fp_on(region='us-east-1')
chech_fp_on(region='ap-northeast-1')