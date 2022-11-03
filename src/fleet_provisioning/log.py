from concurrent.futures import Future
from awsiot import iotidentity
from src.utils.util import print_log
from src.fleet_provisioning import util


class Log:
    def __init__(self, claim_client_name:str) -> None:
        self.__claim_client_name:str = claim_client_name


    def print_published(self, api:str, future:Future) -> None:
        try:
            future.result() # raises exception if publish failed
            self.print_log(verb='Published', message=f'{api} request')
        except Exception as e:
            self.__print_log(verb='Failed', message=f'to publish {api} request')
            util.error(e)


    def print_subscribing_accepted(self, topic:str) -> None:
        self.__print_subscribing(f'{topic} Accepted')


    def print_subscribing_rejected(self, topic:str) -> None:
        self.__print_subscribing(f'{topic} Rejected')


    def __print_subscribing(self, topic:str) -> None:
        self.print_log(verb='Subscribing...', message=f'{topic} topic')


    def print_subscribed(self, topic:str) -> None:
        self.print_log(verb='Subscribed    ', message=topic)

    
    def print_rejected(self, api:str, response:iotidentity.ErrorResponse) -> None:
        # util.error(f"[{self.__claim}] Eroor: {api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")
        self.print_log(
            verb = 'Error',
            message = f"{api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}"
        )


    def print_log(self, verb:str, message:str) -> None:
        print_log(subject=self.__claim_client_name, verb=verb, message=message)