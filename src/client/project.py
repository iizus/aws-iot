# from src.utils.certs import Cert
# from src.client.client import Client
# from src.fleet_provisioning.util import get_current_time

from src.utils import util


class Project:
    config:dict = util.load_json('config.json')

    def __init__(self, name:str=config.get('PROJECT_NAME')) -> None:
        self.name:str = name
        
        util.print_log(
            subject = 'Project',
            verb = 'Set',
            message = f"to {name}"
        )

    # def create_client(self, client_id:str=get_current_time(), cert_dir:str='') -> Client:
    #     cert_dir:str = f'{self.__name}/{cert_dir}{client_id}'
    #     return Client(
    #         project_name = self.__name,
    #         id = self.__name if client_id == '' else client_id,
    #         cert = Cert(cert_dir)
    #     )