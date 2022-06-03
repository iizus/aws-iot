from time import sleep
from concurrent.futures import Future
from awsiot import iotidentity
from awscrt.mqtt import Connection, QoS
from src.utils.util import print_log
from src.fleet_provisioning import util

class FP:
    from uuid import uuid4

    def __init__(self, template_name:str) -> None:
        self.__template_name:str = template_name
        self.__createKeysAndCertificateResponse:iotidentity.CreateKeysAndCertificateResponse = None
        self.__registerThingResponse:iotidentity.RegisterThingResponse = None
        self.__thing_name:str = None


    def provision_thing(
        self,
        connection:Connection,
        template_parameters:str,
        thing_name:str = str(uuid4()),
    ) -> str:
        self.__thing_name:str = thing_name
        provisioned_thing_name:str = self.__provision_by(connection, template_parameters)
        self.__print_log(verb='Success', message=f"fleet provisioning of {provisioned_thing_name}")
        return provisioned_thing_name


    def __provision_by(self, connection:Connection, template_parameters:str) -> str:
        self.__claim:str = connection.client_id
        try:
            # Subscribe to necessary topics.
            # Note that is **is** important to wait for "accepted/rejected" subscriptions
            # to succeed before publishing the corresponding "request".
            client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(connection)
            thing_name:str = self.__subscribe_and_pubrish_topics_by(client, template_parameters)
            return thing_name
        except Exception as e:
            util.error(e)


    def __subscribe_and_pubrish_topics_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict
    ) -> str:
        response:iotidentity.CreateKeysAndCertificateResponse = self.__get_keys_and_certificate_by(client)
        self.__print_log(verb='Saving...', message=f"Certificate ID: {response.certificate_id}")
        self.__print_log(
            verb = 'Saved',
            message = util.save_certs_in(dir='certs/fleet_provisioning/individual', response=response, thing_name=self.__thing_name),
        )
        thing_name:str = self.__register_thing_by(client, template_parameters)
        return thing_name


    def __get_keys_and_certificate_by(self, client:iotidentity.IotIdentityClient) -> iotidentity.CreateKeysAndCertificateResponse:
        self.__subscribe_CreateKeysAndCertificate_topics_by(client)
        self.__subscribe_RegisterThing_topics_by(client)
        self.__create_keys_and_certificate_by(client)
        return self.__createKeysAndCertificateResponse


    def __on_CreateKeysAndCertificate_accepted(
        self,
        response:iotidentity.CreateKeysAndCertificateResponse
    ) -> None:
        try:
            self.__createKeysAndCertificateResponse:iotidentity.CreateKeysAndCertificateResponse = response
        except Exception as e:
            util.error(e)


    def __on_CreateKeysAndCertificate_rejected(self, response:iotidentity.ErrorResponse) -> None:
        self.__print_rejected('CreateKeysAndCertificate', response)


    def __on_RegisterThing_accepted(self, response:iotidentity.RegisterThingResponse) -> None:
        try:
            self.__registerThingResponse:iotidentity.RegisterThingResponse = response
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
    ) -> None:
        self.__publish_CreateKeysAndCertificate_topic_by(client)
        loop_count:int = 0
        while loop_count < 10 and self.__createKeysAndCertificateResponse is None:
            if self.__createKeysAndCertificateResponse is not None: break
            self.__wait_for('createKeysAndCertificateResponse')
            loop_count += 1

        if self.__createKeysAndCertificateResponse is None:
            raise Exception('CreateKeysAndCertificate API did not succeed')


    def __publish_CreateKeysAndCertificate_topic_by(
        self,
        client:iotidentity.IotIdentityClient
    ) -> None:
        self.__print_publishing('CreateKeysAndCertificate')
        future:Future = client.publish_create_keys_and_certificate(
            request = iotidentity.CreateKeysAndCertificateRequest(),
            qos = QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(self.__on_publish_CreateKeysAndCertificate)


    def __register_thing_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict
    ) -> str:
        self.__publish_RegisterThing_topic_by(client, template_parameters)
        loop_count:int = 0
        while loop_count < 10 and self.__registerThingResponse is None:
            if self.__registerThingResponse is not None: break
            self.__wait_for('RegisterThingResponse')
            loop_count += 1
        return self.__registerThingResponse.thing_name


    def __publish_RegisterThing_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict
    ) -> None:
        request:iotidentity.RegisterThingRequest = iotidentity.RegisterThingRequest(
            template_name = self.__template_name,
            certificate_ownership_token = self.__createKeysAndCertificateResponse.certificate_ownership_token,
            parameters = template_parameters,
        )
        self.__print_publishing('RegisterThing')
        future:Future = client.publish_register_thing(
            request = request,
            qos = QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(self.__on_publish_RegisterThing)


    def __on_publish_CreateKeysAndCertificate(self, future:Future) -> None:
        self.__print_published('CreateKeysAndCertificate', future)


    def __on_publish_RegisterThing(self, future:Future) -> None:
        self.__print_published('RegisterThing', future)


    def __print_publishing(self, topic:str) -> None:
        self.__print_log(verb='Publishing...', message=f'{topic} topic')


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


    def __wait_for(self, response:str) -> None:
        self.__print_log(verb='Waiting...', message=response)
        sleep(1)

    
    def __print_rejected(self, api:str, response:iotidentity.ErrorResponse) -> None:
        # util.error(f"[{self.__claim}] Eroor: {api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")
        self.__print_log(verb='Error', message=f"{api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")


    def __print_log(self, verb:str, message:str) -> None:
        print_log(subject=self.__claim, verb=verb, message=message)