from awscrt.http import HttpProxyOptions

class Proxy:
    def __init__(self, name:str, ca:str, number:int=8883, proxy:HttpProxyOptions=None) -> None:
        self.name:str = name
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = proxy



class Port:
    def __init__(self, name:str, ca:str, number:int=8883) -> None:
        self.name:str = name
        self.ca:str = ca
        self.port:int = number
        self.proxy:HttpProxyOptions = None


    def set_proxy(self, host:str, port:int=443) -> Proxy:
        proxy:HttpProxyOptions = HttpProxyOptions(host, port)
        return Proxy(self.name, self.ca, self.port, proxy)



from certs import get_ca_path
ca_path:str = get_ca_path()

class Endpoint:
    def __init__(self, name:str) -> None:
        self.name:str = name
        self.ca:str = ca_path
        self.port:int = 8883
        self.proxy:HttpProxyOptions = None


    def set_port(self, number:int=8883) -> Port:
        return Port(self.name, self.ca, number)

        


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
        name:str = f'{self.__endpoint_prefix}-ats.iot.{region}.amazonaws.com'
        print(f"Endpoint of {region} of {self.__account_name} account: {name}")
        return Endpoint(name)