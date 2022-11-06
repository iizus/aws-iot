from src.utils import util
# from src.client.endpoint import Endpoint


from awsiot import __version__
print(f"Version of AWS IoT Device SDK for Python v2: {__version__}")


class Account:
    DEFAULT:dict = util.load_json('default.json')

    def __init__(
        self,
        name:str = DEFAULT.get('ACCOUNT_NAME'),
        config_path:str = DEFAULT.get('ENDPOINT_FILE_PATH'),
    ) -> None:
        endpoints:dict = util.load_json(config_path)
        self.endpoint_prefix:str = endpoints.get(name)
        util.print_log(subject='Account', verb='Set', message=f"to {name}")


    # def get_account(self) -> str:
    #     return self.__endpoint_prefix



#     def get_endpoint_of(self, region_name:str=DEFAULT.get('REGION_NAME')) -> Endpoint:
#         name:str = f'{self.__endpoint_prefix}-ats.iot.{region_name}.amazonaws.com'
#         return Endpoint(name)


# def get_endpoint(
#     account_name:str = DEFAULT.get('ACCOUNT_NAME'),
#     region_name:str = DEFAULT.get('REGION_NAME'),
# ) -> Endpoint:
#     account:Account = Account(account_name)
#     endpoint:Endpoint = account.get_endpoint_of(region_name)
#     return endpoint