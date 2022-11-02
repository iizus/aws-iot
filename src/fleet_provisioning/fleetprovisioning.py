from typing import Tuple, List
from concurrent.futures import Future
from awsiot import iotidentity
from awscrt.mqtt import QoS
from src.client.connection import Connection
from src.fleet_provisioning.fp import FP


REGISTER_THING:str = 'RegisterThing'
CREATE_KEYS_AND_CERTIFICATE:str = 'CreateKeysAndCertificate'


class FleetProvisioning:
    def __init__(self, template_name:str, thing_name_key:str, claim_connection:Connection)  -> None:
        self.__template_name:str = template_name
        self.__thing_name_key:str = thing_name_key
        self.__claim_connection:Connection = claim_connection
        self.__claim_client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(
            claim_connection.connection
        )
        self.__fp:FP = FP()
    

    def register_thing_by(self, provisioning_thing_name:str) -> str:
        response = self.__fp.request_and_wait(
            claim_connection = self.__claim_connection,
            request_name = REGISTER_THING,
            request = self.__publish_RegisterThing_topic_by,
            template_parameters = { self.__thing_name_key: provisioning_thing_name },
            cert = self.save_keys_and_certificate_by(provisioning_thing_name),
        )
        provisioned_thing_name:str = response.thing_name
        return provisioned_thing_name
    

    def save_keys_and_certificate_by(
        self,
        client_name:str,
    ) -> iotidentity.CreateKeysAndCertificateResponse:
        cert:iotidentity.CreateKeysAndCertificateResponse = self.__fp.create_keys_and_certificate_by(self.__claim_connection)
        self.__fp.save_certs(cert, client_name)
        return cert


    def unsubscribe_all_topics_and_disconnect(self, subscribed_topic_names:List[str]) -> dict:
        for topic in subscribed_topic_names:
            self.__claim_connection.connection.unsubscribe(topic)
        else:
            result:dict = self.__claim_connection.disconnect()
            return result
        
    
    def subscribe_RegisterThing_topics(self) -> Tuple[str]:
        request:iotidentity.RegisterThingSubscriptionRequest = iotidentity.RegisterThingSubscriptionRequest(
            template_name = self.__template_name
        )
        accepted_topic_name:str = self.__fp.subscribe_RegisterThing_accepted_topic_by(
            self.__claim_client,
            request
        )
        rejected_topic_name:str = self.__fp.subscribe_RegisterThing_rejected_topic_by(
            self.__claim_client,
            request
        )
        return (accepted_topic_name, rejected_topic_name)


    def subscribe_CreateKeysAndCertificate_topics(self) -> Tuple[str]:
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
        accepted_topic_name:str = self.__fp.subscribe_CreateKeysAndCertificate_accepted_topic_by(
            self.__claim_client,
            request
        )
        rejected_topic_name:str = self.__fp.subscribe_CreateKeysAndCertificate_rejected_topic_by(
            self.__claim_client,
            request
        )
        return (accepted_topic_name, rejected_topic_name)

    
    def __publish_RegisterThing_topic_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        template_parameters:dict,
        cert:iotidentity.CreateKeysAndCertificateResponse,
    ) -> None:
        request:iotidentity.RegisterThingRequest = iotidentity.RegisterThingRequest(
            template_name = self.__template_name,
            certificate_ownership_token = cert.certificate_ownership_token,
            parameters = template_parameters,
        )
        future:Future = claim_client.publish_register_thing(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
        )
        future.add_done_callback(self.__fp.on_publish_RegisterThing)