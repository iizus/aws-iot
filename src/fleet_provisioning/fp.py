from time import sleep
from typing import Tuple
from concurrent.futures import Future
from awsiot import iotidentity
from awscrt.mqtt import QoS
from src.utils.util import print_log
from src.fleet_provisioning import util


REGISTER_THING:str = 'RegisterThing'
CREATE_KEYS_AND_CERTIFICATE:str = 'CreateKeysAndCertificate'


class FP:
    from src.client.connection import Connection

    def __init__(self, template_name:str) -> None:
        self.__template_name:str = template_name
        self.__response:dict = dict()
    

    def subscribe_RegisterThing_accepted_topic_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        request:iotidentity.RegisterThingRequest
    ) -> str:
        self.__claim:str = claim_client.mqtt_connection.client_id
        self.__print_subscribing_accepted(REGISTER_THING)
        future, topic_name = claim_client.subscribe_to_register_thing_accepted(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_RegisterThing_accepted
        )
        self.__print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name


    def subscribe_RegisterThing_rejected_topic_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        request:iotidentity.RegisterThingRequest
    ) -> str:
        self.__print_subscribing_rejected(REGISTER_THING)
        future, topic_name = claim_client.subscribe_to_register_thing_rejected(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_RegisterThing_rejected
        )
        self.__print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name

    
    def publish_RegisterThing_topic_by(
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
        future.add_done_callback(self.__on_publish_RegisterThing)

    
    def request_and_wait(
        self,
        claim_connection:Connection,
        request_name:str,
        request,
        template_parameters:dict = None,
        cert:iotidentity.CreateKeysAndCertificateResponse = None,
    ):
        self.__response[request_name] = None
        self.__print_log(verb='Publishing...', message=f'{request_name} topic')
        claim_client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(
            claim_connection.connection
        )
        request(claim_client, template_parameters, cert)
        self.__wait_for(request_name)
        return self.__response[request_name]


    def save_certs(
        self,
        cert:iotidentity.CreateKeysAndCertificateResponse,
        provisioning_thing_name:str
    ) -> None:
        self.__print_log(verb='Saving...', message=f"Certificate ID: {cert.certificate_id}")
        log:str = util.save_certs_in(
            dir = 'certs/fleet_provisioning/individual',
            response = cert,
            thing_name = provisioning_thing_name
        )
        self.__print_log(verb='Saved', message=log)


    def subscribe_CreateKeysAndCertificate_topics_by(
        self,
        claim_connection:Connection
    ) -> Tuple[str]:
        claim_client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(
            claim_connection.connection
        )
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
        accepted_topic_name:str = self.__subscribe_CreateKeysAndCertificate_accepted_topic_by(
            claim_client,
            request
        )
        rejected_topic_name:str = self.__subscribe_CreateKeysAndCertificate_rejected_topic_by(
            claim_client,
            request
        )
        return (accepted_topic_name, rejected_topic_name)


    def create_keys_and_certificate_by(
        self,
        claim_connection:Connection,
    ) -> iotidentity.CreateKeysAndCertificateResponse:
        self.request_and_wait(
            claim_connection = claim_connection,
            request_name = CREATE_KEYS_AND_CERTIFICATE,
            request = self.__publish_CreateKeysAndCertificate_topic_by,
        )
        if self.__response[CREATE_KEYS_AND_CERTIFICATE] is None:
            raise Exception(f'{CREATE_KEYS_AND_CERTIFICATE} API did not succeed')
        return self.__response[CREATE_KEYS_AND_CERTIFICATE]
        

    def __on_CreateKeysAndCertificate_accepted(
        self,
        response:iotidentity.CreateKeysAndCertificateResponse
    ) -> None:
        try:
            self.__response[CREATE_KEYS_AND_CERTIFICATE] = response
        except Exception as e:
            util.error(e)


    def __on_CreateKeysAndCertificate_rejected(self, response:iotidentity.ErrorResponse) -> None:
        self.__print_rejected(CREATE_KEYS_AND_CERTIFICATE, response)


    def __on_RegisterThing_accepted(self, response:iotidentity.RegisterThingResponse) -> None:
        try:
            self.__response[REGISTER_THING] = response
        except Exception as e:
            util.error(e)


    def __on_RegisterThing_rejected(self, response:iotidentity.ErrorResponse) -> None:
        self.__print_rejected(REGISTER_THING, response)


    def __subscribe_CreateKeysAndCertificate_accepted_topic_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest
    ) -> str:
        self.__print_subscribing_accepted(CREATE_KEYS_AND_CERTIFICATE)
        future, topic_name = claim_client.subscribe_to_create_keys_and_certificate_accepted(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_CreateKeysAndCertificate_accepted
        )
        self.__print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name


    def __subscribe_CreateKeysAndCertificate_rejected_topic_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest
    ) -> str:
        self.__print_subscribing_rejected(CREATE_KEYS_AND_CERTIFICATE)
        future, topic_name = claim_client.subscribe_to_create_keys_and_certificate_rejected(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_CreateKeysAndCertificate_rejected
        )
        self.__print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name


    def __publish_CreateKeysAndCertificate_topic_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        template_parameters:dict = None,
        cert:iotidentity.CreateKeysAndCertificateResponse = None,
    ) -> None:
        future:Future = claim_client.publish_create_keys_and_certificate(
            request = iotidentity.CreateKeysAndCertificateRequest(),
            qos = QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(self.__on_publish_CreateKeysAndCertificate)


    def __wait_for(self, request_name:str):
        loop_count:int = 0
        while loop_count < 10 and self.__response[request_name] is None:
            if self.__response[request_name] is not None: break
            self.__print_log(verb='Waiting...', message=f'{request_name}Response')
            sleep(1)
            loop_count += 1
        else:
            return self.__response[request_name]


    def __on_publish_CreateKeysAndCertificate(self, future:Future) -> None:
        self.__print_published(CREATE_KEYS_AND_CERTIFICATE, future)


    def __on_publish_RegisterThing(self, future:Future) -> None:
        self.__print_published(REGISTER_THING, future)


    def __print_published(self, api:str, future:Future) -> None:
        try:
            future.result() # raises exception if publish failed
            self.__print_log(verb='Published', message=f'{api} request')
        except Exception as e:
            self.__print_log(verb='Failed', message=f'to publish {api} request')
            util.error(e)


    def __print_subscribing_accepted(self, topic:str) -> None:
            self.__print_subscribing(f'{topic} Accepted')


    def __print_subscribing_rejected(self, topic:str) -> None:
            self.__print_subscribing(f'{topic} Rejected')


    def __print_subscribing(self, topic:str) -> None:
        self.__print_log(verb='Subscribing...', message=f'{topic} topic')


    def __print_subscribed(self, topic:str) -> None:
        self.__print_log(verb='Subscribed', message=topic)

    
    def __print_rejected(self, api:str, response:iotidentity.ErrorResponse) -> None:
        # util.error(f"[{self.__claim}] Eroor: {api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")
        self.__print_log(
            verb = 'Error',
            message = f"{api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}"
        )


    def __print_log(self, verb:str, message:str) -> None:
        print_log(subject=self.__claim, verb=verb, message=message)