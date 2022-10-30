from awscrt.http import HttpProxyOptions
from src.utils import util
from src.client.certs import get_ca_path


class Endpoint:
    def __init__(
        self,
        name:str,
        ca:str = 'RSA2048',
        port:int = 8883,
        proxy:HttpProxyOptions = None,
    ) -> None:
        self.name:str = name
        self.ca:str = ca
        self.ca_path:str = get_ca_path(type=ca)
        self.port:int = port
        self.proxy:HttpProxyOptions = proxy
        self.endpoint:str = f"{self.name}:{self.port}"

        util.print_log(
            subject = 'Endpoint',
            verb = 'Set',
            message = f"to {self.endpoint}, CA path: {self.ca_path}"
        )

    def set_ca(self, type:str='RSA2048'):
        return Endpoint(name=self.name, ca=type, port=self.port, proxy=self.proxy)

    def set_port(self, number:int=8883):
        return Endpoint(name=self.name, ca=self.ca, port=number, proxy=self.proxy)

    def set_proxy(self, host:str, port:int):
        options:HttpProxyOptions = HttpProxyOptions(host_name=host, port=port)
        return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=options)