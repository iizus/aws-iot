from awscrt.http import HttpProxyOptions

class Proxy:
    def __init__(
        self,
        endpoint:str,
        ca:str,
        number:int = 8883,
        proxy:HttpProxyOptions = None,
    ) -> None:
        self.endpoint:str = endpoint
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = proxy



class Port:
    def __init__(self, endpoint:str, ca:str, number:int=8883) -> None:
        self.endpoint:str = endpoint
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = None


    def set_proxy(self, host:str, port:int=443) -> Proxy:
        proxy:HttpProxyOptions = HttpProxyOptions(host, port)
        return Proxy(self.endpoint, self.ca, self.port, proxy)



import certs

class Endpoint:
    def __init__(self, endpoint:str) -> None:
        self.endpoint:str = endpoint
        self.ca:str = certs.get_ca_path()
        self.port:int = 8883
        self.proxy:HttpProxyOptions = None


    def set_port(self, number:int=8883) -> Port:
        return Port(self.endpoint, self.ca, number)

        


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


    def get_endpoint_of(self, region:str='us-east-1') -> Endpoint:
        endpoint:str = f'{self.__endpoint_prefix}-ats.iot.{region}.amazonaws.com'
        region:Endpoint = Endpoint(endpoint)
        print(f"Endpoint of {region} of {self.__account_name} account: {endpoint}")
        return region