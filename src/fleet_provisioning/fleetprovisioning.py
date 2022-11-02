from typing import Tuple, List
from concurrent.futures import Future
from awsiot import iotidentity
from awscrt.mqtt import QoS
from src.fleet_provisioning.fp import FP
from src.fleet_provisioning.util import get_current_time, error


REGISTER_THING:str = 'RegisterThing'
CREATE_KEYS_AND_CERTIFICATE:str = 'CreateKeysAndCertificate'


class FleetProvisioning:
    from src.client.connection import Connection

    def __init__(self, template_name:str, thing_name_key:str) -> None:
        self.__template_name:str = template_name
        self.__thing_name_key:str = thing_name_key
        self.__fp:FP = FP()


    def provision_thing(self, claim_connection:Connection, name:str=get_current_time()) -> str:
        try:
            # Subscribe to necessary topics.
            # Note that is **is** important to wait for "accepted/rejected" subscriptions
            # to succeed before publishing the corresponding "request".
            subscribed_topic_names:List[str] = self.subscribe_all_topics(claim_connection)
            provisioned_thing_name:str = self.register_thing_by(
                claim_connection = claim_connection,
                provisioning_thing_name = name,
            )
            # self.__print_log(verb='Success', message=f"fleet provisioning of {provisioned_thing_name}")
            self.unsubscribe_all_topics_and_disconnect(claim_connection, subscribed_topic_names)
        except Exception as e:
            error(e)
        return provisioned_thing_name


    def register_thing_by(
        self,
        claim_connection:Connection,
        provisioning_thing_name:str
    ) -> str:
        # subscribed_topic_names:Tuple[str] = self.__subscribe_RegisterThing_topics_by(
        #     claim_connection
        # )
        provisioned_thing_name:str = self.__wait_register_thing(
            claim_connection,
            provisioning_thing_name
        )
        return provisioned_thing_name
    

    def save_keys_and_certificate_by(
        self,
        claim_connection:Connection,
        client_name:str,
    ) -> iotidentity.CreateKeysAndCertificateResponse:
        # subscribed_topic_names:Tuple[str] = self.__subscribe_CreateKeysAndCertificate_topics_by(
        #     claim_connection
        # )
        cert:iotidentity.CreateKeysAndCertificateResponse = self.__fp.create_keys_and_certificate_by(claim_connection)
        self.__fp.save_certs(cert, client_name)
        return cert


    def subscribe_all_topics(self, claim_connection:Connection) -> List[str]:
        self.__subscribed_topic_names:List[str] = list()
        self.__subscribed_topic_names += self.__subscribe_CreateKeysAndCertificate_topics_by(
            claim_connection
        )
        self.__subscribed_topic_names += self.__subscribe_RegisterThing_topics_by(
            claim_connection
        )
        return self.__subscribed_topic_names

    
    def unsubscribe_all_topics_and_disconnect(
        self,
        claim_connection:Connection, 
        subscribed_topic_names:List[str],
    ) -> dict:
        for topic in subscribed_topic_names:
            claim_connection.connection.unsubscribe(topic)
        else:
            result:dict = claim_connection.disconnect()
            return result


    def __wait_register_thing(
        self,
        claim_connection:Connection,
        provisioning_thing_name:str
    ) -> str:
        response = self.__fp.request_and_wait(
            claim_connection = claim_connection,
            request_name = REGISTER_THING,
            request = self.__publish_RegisterThing_topic_by,
            template_parameters = { self.__thing_name_key: provisioning_thing_name },
            cert = self.save_keys_and_certificate_by(
                claim_connection,
                provisioning_thing_name
            ),
        )
        provisioned_thing_name:str = response.thing_name
        return provisioned_thing_name
        
    
    def __subscribe_RegisterThing_topics_by(self, claim_connection:Connection) -> Tuple[str]:
        request:iotidentity.RegisterThingSubscriptionRequest = iotidentity.RegisterThingSubscriptionRequest(
            template_name = self.__template_name
        )
        claim_client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(
            claim_connection.connection
        )
        accepted_topic_name:str = self.__fp.subscribe_RegisterThing_accepted_topic_by(
            claim_client,
            request
        )
        rejected_topic_name:str = self.__fp.subscribe_RegisterThing_rejected_topic_by(
            claim_client,
            request
        )
        return (accepted_topic_name, rejected_topic_name)


    def __subscribe_CreateKeysAndCertificate_topics_by(
        self,
        claim_connection:Connection
    ) -> Tuple[str]:
        claim_client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(
            claim_connection.connection
        )
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
        accepted_topic_name:str = self.__fp.subscribe_CreateKeysAndCertificate_accepted_topic_by(
            claim_client,
            request
        )
        rejected_topic_name:str = self.__fp.subscribe_CreateKeysAndCertificate_rejected_topic_by(
            claim_client,
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