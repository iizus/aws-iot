from awscrt.http import HttpProxyOptions
from src.utils import util
from src.client.certs import get_ca_path
from src.client.account import Account


class Endpoint:
    DEFAULT:dict = util.load_json('default.json')

    def __init__(
        self,
        accout:Account,
        region_name:str = DEFAULT.get('REGION_NAME'),
        ca:str = DEFAULT.get('CA'),
        port:int = DEFAULT.get('PORT'),
        proxy:HttpProxyOptions = None,
    ) -> None:
        self.name:str = f'{accout.endpoint_prefix}-ats.iot.{region_name}.amazonaws.com'
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

    # def set_ca(self, type:str='RSA2048'):
    #     return Endpoint(name=self.name, ca=type, port=self.port, proxy=self.proxy)

    # def set_port(self, number:int=8883):
    #     return Endpoint(name=self.name, ca=self.ca, port=number, proxy=self.proxy)

    # def set_proxy(self, host:str, port:int):
    #     options:HttpProxyOptions = HttpProxyOptions(host_name=host, port=port)
    #     return Endpoint(name=self.name, ca=self.ca, port=self.port, proxy=options)