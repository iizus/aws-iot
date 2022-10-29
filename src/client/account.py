from src.utils import util
from src.client.endpoint import Endpoint


DEFAULT_ACCOUNT_NAME:str = 'isengard'
DEFAULT_REGION_NAME:str = 'us-east-1'

from awsiot import __version__
print(f"Version of AWS IoT Device SDK for Python v2: {__version__}")

class Account:
    def __init__(self, name:str=DEFAULT_ACCOUNT_NAME, config_path:str='endpoint.json') -> None:
        endpoints:dict = util.load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        util.print_log(subject='Account', verb='Set', message=f"to {name}")


    def get_endpoint_of(self, region_name:str=DEFAULT_REGION_NAME) -> Endpoint:
        name:str = f'{self.__endpoint_prefix}-ats.iot.{region_name}.amazonaws.com'
        return Endpoint(name)


def check_communication(account_name:str=DEFAULT_ACCOUNT_NAME) -> None:
    get_endpoint_of(account_name).check_communication()


def get_endpoint_of(
    account_name:str = DEFAULT_ACCOUNT_NAME,
    region_name:str = DEFAULT_REGION_NAME
) -> Endpoint:
    env:Account = Account(account_name)
    endpoint:Endpoint = env.get_endpoint_of(region_name)
    return endpoint