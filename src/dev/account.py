from endpoint import Endpoint

from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from utils.util import load_json



class Account:
    def __init__(self, name:str='test', config_path:str='endpoint.json') -> None:
        self.__account_name = name
        endpoints:dict = load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        print(f"Account: {name}")


    def get_endpoint(self, region:str='us-east-1') -> Endpoint:
        endpoint:str = f'{self.__endpoint_prefix}-ats.iot.{region}.amazonaws.com'
        region:Endpoint = Endpoint(endpoint)
        print(f"Endpoint of {region} of {self.__account_name} account: {endpoint}")
        return region