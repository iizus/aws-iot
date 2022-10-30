from src.utils import util
from src.client.pubsub import PubSub
from src.client.endpoint import Endpoint


DEFAULT_ACCOUNT_NAME:str = 'isengard'
DEFAULT_REGION_NAME:str = 'us-east-1'
DEFAULT_ENDPOINT_FILE_PATH:str = 'endpoint.json'

DEFAULT_TOPIC:str = 'check/communication'
DEFAULT_TEMPLATE_NAME:str = 'aws-iot'
DEFAULT_THING_NAME_KEY:str = 'device_id'


from awsiot import __version__
print(f"Version of AWS IoT Device SDK for Python v2: {__version__}")


class Account:
    def __init__(
        self,
        name:str = DEFAULT_ACCOUNT_NAME,
        config_path:str = DEFAULT_ENDPOINT_FILE_PATH,
    ) -> None:
        endpoints:dict = util.load_json(config_path)
        self.__endpoint_prefix:str = endpoints.get(name)
        util.print_log(subject='Account', verb='Set', message=f"to {name}")


    def get_endpoint_of(self, region_name:str=DEFAULT_REGION_NAME) -> Endpoint:
        name:str = f'{self.__endpoint_prefix}-ats.iot.{region_name}.amazonaws.com'
        return Endpoint(name)


def check_communication(
    account_name:str = DEFAULT_ACCOUNT_NAME,
    region_name:str = DEFAULT_REGION_NAME,
    template_name:str = DEFAULT_TEMPLATE_NAME,
    thing_name_key:str = DEFAULT_THING_NAME_KEY,
    topic_name:str = DEFAULT_TOPIC,
):
    endpoint:Endpoint = get_endpoint(account_name, region_name)
    pubsub:PubSub = PubSub(endpoint, template_name, thing_name_key, topic_name)
    result = pubsub.check_communication()
    return result


def get_endpoint(
    account_name:str = DEFAULT_ACCOUNT_NAME,
    region_name:str = DEFAULT_REGION_NAME,
) -> Endpoint:
    account:Account = Account(account_name)
    endpoint:Endpoint = account.get_endpoint_of(region_name)
    return endpoint