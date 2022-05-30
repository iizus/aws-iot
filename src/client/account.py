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
        print(f"[Endpoint] Set to {self.name}:{self.port}")


    def set_proxy(self, host:str, port:int=443) -> Proxy:
        proxy:HttpProxyOptions = HttpProxyOptions(host, port)
        print(f"[Endpoint ]Set HTTP proxy as {host}:{port} for {self.name}:{self.port}")
        return Proxy(self.name, self.ca, self.port, proxy)



class Endpoint:
    from src.client.certs import get_ca_path
    ca_path:str = get_ca_path()

    def __init__(self, name:str) -> None:
        self.name:str = name
        self.ca:str = self.ca_path
        self.port:int = 8883
        self.proxy:HttpProxyOptions = None
        print(f"[Endpoint] Set to {self.name}:{self.port}")


    def set_port(self, number:int=8883) -> Port:
        return Port(self.name, self.ca, number)

        

# from sys import path
# from os.path import dirname
# current_dir:str = path[0]
# parent_dir:str = dirname(current_dir)
# path.append(parent_dir)

from src.utils.util import load_json

class Account:
    def __init__(self, name:str='test', config_path:str='endpoint.json') -> None:
        endpoints:dict = load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        print(f"[Account] Set to {name}")


    def get_endpoint_of(self, region:str='us-east-1') -> Endpoint:
        name:str = f'{self.__endpoint_prefix}-ats.iot.{region}.amazonaws.com'
        return Endpoint(name)