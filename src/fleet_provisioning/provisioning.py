from typing import Tuple, List
from awsiot import iotidentity

from src.utils import util
from src.client.client import Client
from src.client.connection import Connection
from src.fleet_provisioning.util import get_current_time
from src.client.project import Project
from src.client.account import get_endpoint, Endpoint
from src.fleet_provisioning.fp import FP


REGISTER_THING:str = 'RegisterThing'
CREATE_KEYS_AND_CERTIFICATE:str = 'CreateKeysAndCertificate'

DEFAULT:dict = util.load_json('default.json')


class Provisioning:
    def __init__(
        self,
        endpoint:Endpoint = get_endpoint(),
        template_name:str = DEFAULT.get('TEMPLATE_NAME'),
        thing_name_key:str = DEFAULT.get('THING_NAME_KEY'),
    ) -> None:
        self.__template_name:str = template_name
        self.__thing_name_key:str = thing_name_key
        self.__project:Project = Project(name='fleet_provisioning')
        self.__claim_client:Client = self.__project.create_client(client_id='claim')
        claim_connection:Connection = self.__claim_client.connect_to(endpoint)
        self.__connection = claim_connection.connection
        self.__fp:FP = FP(self.__connection)
        self.__subscribed_topic_names:List[str] = list()


    def provision_thing(self, name:str=get_current_time()) -> Client:
        self.subscribe_all_topics()
        provisioned_thing:str = self.register_thing_as(name)
        self.unsubscribe_all_topics_and_disconnect()
        return provisioned_thing


    def subscribe_all_topics(self) -> List[str]:
        self.__subscribed_topic_names += self.__subscribe_CreateKeysAndCertificate_topics()
        self.__subscribed_topic_names += self.__subscribe_RegisterThing_topics()
        return self.__subscribed_topic_names


    def register_thing_as(self, name:str = get_current_time()) -> Client:
        util.print_log(subject=name, verb='Provisioning...')
        provisioned_thing:Client = self.__project.create_client(
            client_id = self.__register_thing_as(name),
            cert_dir = 'individual/'
        )
        util.print_log(subject=name, verb='Provisioned successfully')
        return provisioned_thing

    
    def unsubscribe_all_topics_and_disconnect(self) -> dict:
        for topic_name in self.__subscribed_topic_names:
            self.__print_claim_log('Unsubscribing...', topic_name)
            self.__connection.unsubscribe(topic_name)
            self.__print_claim_log('Unsubscribed    ', topic_name)
        else:
            result:dict = self.__claim_client.disconnect()
            return result

    
    def __print_claim_log(self, verb:str, topic_name:str) -> None:
        util.print_log(subject=self.__claim_client.id, verb=verb, message=topic_name)


    def __register_thing_as(self, provisioning_thing_name:str) -> str:
        response = self.__fp.request_and_wait(
            request_name = REGISTER_THING,
            request = self.__publish_RegisterThing_topic_by,
            template_parameters = { self.__thing_name_key: provisioning_thing_name },
            cert = self.save_keys_and_certificate_by(provisioning_thing_name),
        )
        provisioned_thing_name:str = response.thing_name
        return provisioned_thing_name
    

    def save_keys_and_certificate_by(self, client_name:str) -> iotidentity.CreateKeysAndCertificateResponse:
        cert:iotidentity.CreateKeysAndCertificateResponse = self.__fp.create_keys_and_certificate()
        self.__fp.save_certs(cert, client_name)
        return cert
        
    
    def __subscribe_RegisterThing_topics(self) -> Tuple[str]:
        request:iotidentity.RegisterThingSubscriptionRequest = iotidentity.RegisterThingSubscriptionRequest(
            self.__template_name
        )
        accepted_topic_name:str = self.__fp.subscribe_RegisterThing_accepted_topic_by(request)
        rejected_topic_name:str = self.__fp.subscribe_RegisterThing_rejected_topic_by(request)
        return (accepted_topic_name, rejected_topic_name)


    def __subscribe_CreateKeysAndCertificate_topics(self) -> Tuple[str]:
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
        accepted_topic_name:str = self.__fp.subscribe_CreateKeysAndCertificate_accepted_topic_by(request)
        rejected_topic_name:str = self.__fp.subscribe_CreateKeysAndCertificate_rejected_topic_by(request)
        return (accepted_topic_name, rejected_topic_name)

    
    def __publish_RegisterThing_topic_by(
        self,
        template_parameters:dict,
        cert:iotidentity.CreateKeysAndCertificateResponse,
    ) -> None:
        request:iotidentity.RegisterThingRequest = iotidentity.RegisterThingRequest(
            template_name = self.__template_name,
            certificate_ownership_token = cert.certificate_ownership_token,
            parameters = template_parameters,
        )
        self.__fp.publish_RegisterThing_topic_by(request)