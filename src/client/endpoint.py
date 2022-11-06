from awscrt.http import HttpProxyOptions

from src.utils import util, certs
from src.client.account import Account


class Endpoint:
    config:dict = util.load_json('config.json')

    def __init__(
        self,
        accout:Account = Account(),
        region_name:str = config.get('REGION_NAME'),
        ca:str = config.get('CA'),
        port:int = config.get('PORT'),
        proxy:HttpProxyOptions = None,
    ) -> None:
        self.name:str = f'{accout.endpoint_prefix}-ats.iot.{region_name}.amazonaws.com'
        self.ca:str = ca
        self.ca_path:str = certs.get_ca_path(type=ca)
        self.port:int = port
        self.proxy:HttpProxyOptions = proxy
        self.endpoint:str = f"{self.name}:{self.port}"

        util.print_log(
            subject = 'Endpoint',
            verb = 'Set',
            message = f"to {self.endpoint}, CA path: {self.ca_path}"
        )