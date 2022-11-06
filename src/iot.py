from src.utils.util import load_json
# from src.utils import util
from src.client.account import Account
from src.client.endpoint import Endpoint
from src.client.project import Project
# from src.client.client import Client
# from src.fleet_provisioning.util import get_current_time
# from src.fleet_provisioning.provisioning import Provisioning


class IoT:
    def __init__(self, config_path:str) -> None:
        config:dict = load_json(config_path)
        self.__account:Account = self.__set_account_as(config)
        self.__endpoint:Endpoint = self.__set_endpoint_as(config)
        self.__project:Project = self.__set_project_as(config)

    def get_account(self, name:str) -> Account:
        return Account(name)

    def __set_account_as(self, config:dict) -> Account:
        return self.get_account(name=config.get('ACCOUNT_NAME'))

    def get_endpoint(self, region_name:str, ca:str, port:int) -> Endpoint:
        return Endpoint(
            name = self.__account.get_endpoint_of(region_name),
            ca = ca,
            port = port,
        )

    def __set_endpoint_as(self, config:dict) -> Endpoint:
        return self.get_endpoint(
            region_name = config.get('REGION_NAME'),
            ca = config.get('CA'),
            port = config.get('PORT'),
        )

    def get_project(self, name:str) -> Project:
        return Project(name)

    def __set_project_as(self, config:dict) -> Account:
        return self.get_project(name=config.get('PROJECT_NAME'))