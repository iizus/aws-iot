from time import sleep
from concurrent.futures import Future
from awsiot import iotidentity
from awscrt.mqtt import QoS
from src.fleet_provisioning.log import Log
from src.fleet_provisioning import util


REGISTER_THING:str = 'RegisterThing'
CREATE_KEYS_AND_CERTIFICATE:str = 'CreateKeysAndCertificate'


class FP:
    def __init__(self, claim_client:iotidentity.IotIdentityClient) -> None:
        self.__claim_client:iotidentity.IotIdentityClient = claim_client
        self.__log:Log = Log(claim_client_name=claim_client.mqtt_connection.client_id)
        self.__response:dict = dict()
    

    def subscribe_RegisterThing_accepted_topic_by(self, request:iotidentity.RegisterThingRequest) -> str:
        self.__log.print_subscribing_accepted(REGISTER_THING)
        future, topic_name = self.__claim_client.subscribe_to_register_thing_accepted(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_RegisterThing_accepted
        )
        self.__log.print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name


    def subscribe_RegisterThing_rejected_topic_by(self, request:iotidentity.RegisterThingRequest) -> str:
        self.__log.print_subscribing_rejected(REGISTER_THING)
        future, topic_name = self.__claim_client.subscribe_to_register_thing_rejected(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_RegisterThing_rejected
        )
        self.__log.print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name

    
    def request_and_wait(
        self,
        request_name:str,
        request,
        template_parameters:dict = None,
        cert:iotidentity.CreateKeysAndCertificateResponse = None,
    ):
        self.__response[request_name] = None
        self.__log.print_log(verb='Publishing...', message=f'{request_name} topic')
        request(template_parameters, cert)
        self.__wait_for(request_name)
        return self.__response[request_name]


    def save_certs(
        self,
        cert:iotidentity.CreateKeysAndCertificateResponse,
        provisioning_thing_name:str
    ) -> None:
        self.__log.print_log(verb='Saving...', message=f"Certificate ID: {cert.certificate_id}")
        log:str = util.save_certs_in(
            dir = 'certs/fleet_provisioning/individual',
            response = cert,
            thing_name = provisioning_thing_name
        )
        self.__log.print_log(verb='Saved', message=log)


    def create_keys_and_certificate(self) -> iotidentity.CreateKeysAndCertificateResponse:
        self.request_and_wait(
            request_name = CREATE_KEYS_AND_CERTIFICATE,
            request = self.__publish_CreateKeysAndCertificate_topic_by,
        )
        if self.__response[CREATE_KEYS_AND_CERTIFICATE] is None:
            raise Exception(f'{CREATE_KEYS_AND_CERTIFICATE} API did not succeed')
        return self.__response[CREATE_KEYS_AND_CERTIFICATE]

    
    def subscribe_CreateKeysAndCertificate_accepted_topic_by(
        self,
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest
    ) -> str:
        self.__log.print_subscribing_accepted(CREATE_KEYS_AND_CERTIFICATE)
        future, topic_name = self.__claim_client.subscribe_to_create_keys_and_certificate_accepted(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_CreateKeysAndCertificate_accepted
        )
        self.__log.print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name


    def subscribe_CreateKeysAndCertificate_rejected_topic_by(
        self,
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest,
    ) -> str:
        self.__log.print_subscribing_rejected(CREATE_KEYS_AND_CERTIFICATE)
        future, topic_name = self.__claim_client.subscribe_to_create_keys_and_certificate_rejected(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
            callback = self.__on_CreateKeysAndCertificate_rejected
        )
        self.__log.print_subscribed(topic_name)
        future.result() # Wait for subscription to succeed
        return topic_name


    def publish_RegisterThing_topic_by(self, request:iotidentity.RegisterThingRequest) -> None:
        future:Future = self.__claim_client.publish_register_thing(
            request = request,
            qos = QoS.AT_LEAST_ONCE,
        )
        future.add_done_callback(self.__on_publish_RegisterThing)


    def __on_CreateKeysAndCertificate_accepted(self, response:iotidentity.CreateKeysAndCertificateResponse) -> None:
        try:
            self.__response[CREATE_KEYS_AND_CERTIFICATE] = response
        except Exception as e:
            util.error(e)


    def __on_CreateKeysAndCertificate_rejected(self, response:iotidentity.ErrorResponse) -> None:
        self.__log.print_rejected(CREATE_KEYS_AND_CERTIFICATE, response)


    def __on_RegisterThing_accepted(self, response:iotidentity.RegisterThingResponse) -> None:
        try:
            self.__response[REGISTER_THING] = response
        except Exception as e:
            util.error(e)


    def __on_RegisterThing_rejected(self, response:iotidentity.ErrorResponse) -> None:
        self.__log.print_rejected(REGISTER_THING, response)


    def __publish_CreateKeysAndCertificate_topic_by(
        self,
        template_parameters:dict = None,
        cert:iotidentity.CreateKeysAndCertificateResponse = None,
    ) -> None:
        future:Future = self.__claim_client.publish_create_keys_and_certificate(
            request = iotidentity.CreateKeysAndCertificateRequest(),
            qos = QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(self.__on_publish_CreateKeysAndCertificate)


    def __wait_for(self, request_name:str):
        loop_count:int = 0
        while loop_count < 10 and self.__response[request_name] is None:
            if self.__response[request_name] is not None: break
            self.__log.print_log(verb='Waiting...', message=f'{request_name}Response')
            sleep(1)
            loop_count += 1
        else:
            return self.__response[request_name]


    def __on_publish_CreateKeysAndCertificate(self, future:Future) -> None:
        self.__log.print_published(CREATE_KEYS_AND_CERTIFICATE, future)


    def __on_publish_RegisterThing(self, future:Future) -> None:
        self.__log.print_published(REGISTER_THING, future)