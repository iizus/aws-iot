from time import sleep
from concurrent.futures import Future
from awsiot import iotidentity
from awscrt.mqtt import QoS
from src.utils.util import print_log
from src.fleet_provisioning import util


class FP:
    def __init__(self, template_name:str, thing_name_key:str) -> None:
        self.__template_name:str = template_name
        self.__thing_name_key:str = thing_name_key
        self.__response:dict = dict()

        
    def register_thing_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        provisioning_thing_name:str,
    ) -> str:
        self.__claim:str = claim_client.mqtt_connection.client_id
        self.__subscribe_RegisterThing_topics_by(claim_client)
        self.__request_and_wait(
            client = claim_client,
            request_name = 'RegisterThing',
            request = self.__publish_RegisterThing_topic_by,
            template_parameters = { self.__thing_name_key: provisioning_thing_name },
            cert = self.__get_keys_and_certificate_by(claim_client, provisioning_thing_name),
        )
        provisioned_thing_name:str = self.__response['RegisterThing'].thing_name
        return provisioned_thing_name


    def __get_keys_and_certificate_by(
        self,
        claim_client:iotidentity.IotIdentityClient,
        provisioning_thing_name:str
    ) -> iotidentity.CreateKeysAndCertificateResponse:
        self.__subscribe_CreateKeysAndCertificate_topics_by(claim_client)
        cert:iotidentity.CreateKeysAndCertificateResponse = self.__create_keys_and_certificate_by(claim_client)
        self.__save_certs(cert, provisioning_thing_name)
        return cert


    def __save_certs(
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


    def __on_CreateKeysAndCertificate_accepted(
        self,
        response:iotidentity.CreateKeysAndCertificateResponse
    ) -> None:
        try:
            self.__response['CreateKeysAndCertificate'] = response
        except Exception as e:
            util.error(e)


    def __on_CreateKeysAndCertificate_rejected(self, response:iotidentity.ErrorResponse) -> None:
        self.__print_rejected('CreateKeysAndCertificate', response)


    def __on_RegisterThing_accepted(self, response:iotidentity.RegisterThingResponse) -> None:
        try:
            self.__response['RegisterThing'] = response
        except Exception as e:
            util.error(e)


    def __on_RegisterThing_rejected(self, response:iotidentity.ErrorResponse) -> None:
        self.__print_rejected('RegisterThing', response)


    def __subscribe_CreateKeysAndCertificate_topics_by(
        self,
        client:iotidentity.IotIdentityClient
    ) -> None:
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
        self.__subscribe_CreateKeysAndCertificate_accepted_topic_by(client, request)
        self.__subscribe_CreateKeysAndCertificate_rejected_topic_by(client, request)


    def __subscribe_CreateKeysAndCertificate_accepted_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest
    ) -> None:
        self.__print_subscribing_accepted('CreateKeysAndCertificate')
        future, topic = client.subscribe_to_create_keys_and_certificate_accepted(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_CreateKeysAndCertificate_accepted
        )
        self.__print_subscribed(topic)
        future.result() # Wait for subscription to succeed


    def __subscribe_CreateKeysAndCertificate_rejected_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest
    ) -> None:
        self.__print_subscribing_rejected('CreateKeysAndCertificate')
        future, topic = client.subscribe_to_create_keys_and_certificate_rejected(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_CreateKeysAndCertificate_rejected
        )
        self.__print_subscribed(topic)
        future.result() # Wait for subscription to succeed


    def __subscribe_RegisterThing_topics_by(self, client:iotidentity.IotIdentityClient) -> None:
        request:iotidentity.RegisterThingSubscriptionRequest = iotidentity.RegisterThingSubscriptionRequest(
            template_name = self.__template_name
        )
        self.__subscribe_RegisterThing_accepted_topic_by(client, request)
        self.__subscribe_RegisterThing_rejected_topic_by(client, request)


    def __subscribe_RegisterThing_accepted_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        request:iotidentity.RegisterThingRequest
    ) -> None:
        self.__print_subscribing_accepted('RegisterThing')
        future, topic = client.subscribe_to_register_thing_accepted(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_RegisterThing_accepted
        )
        self.__print_subscribed(topic)
        future.result() # Wait for subscription to succeed


    def __subscribe_RegisterThing_rejected_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        request:iotidentity.RegisterThingRequest
    ) -> None:
        self.__print_subscribing_rejected('RegisterThing')
        future, topic = client.subscribe_to_register_thing_rejected(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_RegisterThing_rejected
        )
        self.__print_subscribed(topic)
        future.result() # Wait for subscription to succeed


    def __create_keys_and_certificate_by(
        self,
        client:iotidentity.IotIdentityClient
    ) -> iotidentity.CreateKeysAndCertificateResponse:
        self.__request_and_wait(
            client = client,
            request_name = 'CreateKeysAndCertificate',
            request = self.__publish_CreateKeysAndCertificate_topic_by,
        )
        if self.__response['CreateKeysAndCertificate'] is None:
            raise Exception('CreateKeysAndCertificate API did not succeed')
        return self.__response['CreateKeysAndCertificate']


    def __publish_CreateKeysAndCertificate_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict = None,
        cert:iotidentity.CreateKeysAndCertificateResponse = None,
    ) -> None:
        future:Future = client.publish_create_keys_and_certificate(
            request = iotidentity.CreateKeysAndCertificateRequest(),
            qos = QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(self.__on_publish_CreateKeysAndCertificate)


    def __request_and_wait(
        self,
        client:iotidentity.IotIdentityClient,
        request_name:str,
        request,
        template_parameters:dict = None,
        cert:iotidentity.CreateKeysAndCertificateResponse = None,
    ) -> None:
        self.__response[request_name] = None
        self.__print_log(verb='Publishing...', message=f'{request_name} topic')
        request(client, template_parameters, cert)
        self.__wait_for(request_name)


    def __wait_for(self, request_name:str) -> None:
        loop_count:int = 0
        while loop_count < 10 and self.__response[request_name] is None:
            if self.__response[request_name] is not None: break
            self.__print_log(verb='Waiting...', message=f'{request_name}Response')
            sleep(1)
            loop_count += 1


    def __publish_RegisterThing_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict,
        cert:iotidentity.CreateKeysAndCertificateResponse,
    ) -> None:
        request:iotidentity.RegisterThingRequest = iotidentity.RegisterThingRequest(
            template_name = self.__template_name,
            certificate_ownership_token = cert.certificate_ownership_token,
            parameters = template_parameters,
        )
        future:Future = client.publish_register_thing(
            request = request,
            qos = QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(self.__on_publish_RegisterThing)


    def __on_publish_CreateKeysAndCertificate(self, future:Future) -> None:
        self.__print_published('CreateKeysAndCertificate', future)


    def __on_publish_RegisterThing(self, future:Future) -> None:
        self.__print_published('RegisterThing', future)


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
        self.__print_log(verb='Error', message=f"{api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")


    def __print_log(self, verb:str, message:str) -> None:
        print_log(subject=self.__claim, verb=verb, message=message)