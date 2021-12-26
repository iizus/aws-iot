from multiprocessing.connection import Connection
from awscrt import io, mqtt
from awsiot import iotidentity, mqtt_connection_builder
from concurrent.futures import Future
from threading import Event
from uuid import uuid4
import json
import fp


class FleetProvisioning:
    def __init__(self, endpoint:str, template_name:str) -> None:
        self.__endpoint = endpoint
        self.__template_name = template_name

        self.__is_sample_done:Event = Event()
        self.__createKeysAndCertificateResponse:iotidentity.CreateKeysAndCertificateResponse = None
        self.__registerThingResponse:iotidentity.RegisterThingResponse = None


    def __disconnect(self, mqtt_connection:Connection):
        locked_data:fp.LockedData = fp.LockedData()
        with locked_data.lock:
            if not locked_data.disconnect_called:
                print("Disconnecting...")
                locked_data.disconnect_called = True
                future:Future = mqtt_connection.disconnect()
                future.add_done_callback(self.on_disconnected)

        
    def on_disconnected(self, future:Future) -> None:
        print("Disconnected")
        self.__is_sample_done.set() # Signal that sample is finished


    def on_CreateKeysAndCertificate_accepted(
        self,
        response:iotidentity.CreateKeysAndCertificateResponse
    ) -> None:
        try:
            self.__createKeysAndCertificateResponse:iotidentity.CreateKeysAndCertificateResponse = response
            print(f"Certificate ID: {response.certificate_id}")
            fp.save_certs_based_on(response)
            return
        except Exception as e:
            fp.error(e)


    def on_CreateKeysAndCertificate_rejected(self, response:iotidentity.ErrorResponse) -> None:
        fp.print_rejected('CreateKeysAndCertificate', response)


    def on_RegisterThing_accepted(self, response:iotidentity.RegisterThingResponse) -> None:
        try:
            self.__registerThingResponse:iotidentity.RegisterThingResponse = response
            print(f"Thing name: {response.thing_name}")
            return
        except Exception as e:
            fp.error(e)


    def on_RegisterThing_rejected(self, response:iotidentity.ErrorResponse) -> None:
        fp.print_rejected('RegisterThing', response)


    def __create_connection_with(
        self,
        client_id:str,
        cert:str,
        key:str,
        ca:str,
    ) -> Connection:
        # Spin up resources
        event_loop_group:io.EventLoopGroup = io.EventLoopGroup(1)
        host_resolver:io.DefaultHostResolver = io.DefaultHostResolver(event_loop_group)

        connection:Connection = mqtt_connection_builder.mtls_from_path(
            endpoint = self.__endpoint,
            cert_filepath = cert,
            pri_key_filepath = key,
            client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver),
            ca_filepath = ca,
            client_id = client_id,
            on_connection_interrupted = fp.on_connection_interrupted,
            on_connection_resumed = fp.on_connection_resumed,
            clean_session = False,
            keep_alive_secs = 30,
            http_proxy_options = None,
        )
        print(f"Connecting to {self.__endpoint} with client ID '{client_id}'...")
        return connection


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
        future, topic = client.subscribe_to_create_keys_and_certificate_accepted(
            request = request,
            qos = mqtt.QoS.AT_LEAST_ONCE,
            callback = self.on_CreateKeysAndCertificate_accepted
        )
        print(f"Subscribed {topic}")
        future.result() # Wait for subscription to succeed


    def __subscribe_CreateKeysAndCertificate_rejected_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        request:iotidentity.CreateKeysAndCertificateSubscriptionRequest
    ) -> None:
        future, topic = client.subscribe_to_create_keys_and_certificate_rejected(
            request = request,
            qos = mqtt.QoS.AT_LEAST_ONCE,
            callback = self.on_CreateKeysAndCertificate_rejected
        )
        print(f"Subscribed {topic}")
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
        future, topic = client.subscribe_to_register_thing_accepted(
            request = request,
            qos = mqtt.QoS.AT_LEAST_ONCE,
            callback = self.on_RegisterThing_accepted
        )
        print(f"Subscribed {topic}")
        future.result() # Wait for subscription to succeed


    def __subscribe_RegisterThing_rejected_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        request:iotidentity.RegisterThingRequest
    ) -> None:
        print("Subscribing to CreateKeysAndCertificate Rejected topic...")
        future, topic = client.subscribe_to_register_thing_rejected(
            request = request,
            qos = mqtt.QoS.AT_LEAST_ONCE,
            callback = self.on_RegisterThing_rejected
        )
        print(f"Subscribed {topic}")
        future.result() # Wait for subscription to succeed


    def __publish_CreateKeysAndCertificate_topic_by(
        self,
        client:iotidentity.IotIdentityClient
    ) -> None:
        self.__CreateKeysAndCertificate_topic_by(client)
        loop_count:int = 0
        while loop_count < 10 and self.__createKeysAndCertificateResponse is None:
            if self.__createKeysAndCertificateResponse is not None: break
            fp.wait_for(self.__createKeysAndCertificateResponse)
            loop_count += 1

        if self.__createKeysAndCertificateResponse is None:
            raise Exception('CreateKeysAndCertificate API did not succeed')


    def __CreateKeysAndCertificate_topic_by(
        self,
        client:iotidentity.IotIdentityClient
    ) -> None:
        print("Publishing to CreateKeysAndCertificate...")
        future:Future = client.publish_create_keys_and_certificate(
            request = iotidentity.CreateKeysAndCertificateRequest(),
            qos = mqtt.QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(fp.on_publish_CreateKeysAndCertificate)


    def __publish_RegisterThing_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict
    ) -> None:
        self.__RegisterThing_topic_by(client, template_parameters)
        loop_count:int = 0
        while loop_count < 10 and self.__registerThingResponse is None:
            if self.__registerThingResponse is not None: break
            fp.wait_for(self.__registerThingResponse)
            loop_count += 1


    def __RegisterThing_topic_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict
    ) -> None:
        request:iotidentity.RegisterThingRequest = iotidentity.RegisterThingRequest(
            template_name = self.__template_name,
            certificate_ownership_token = self.__createKeysAndCertificateResponse.certificate_ownership_token,
            parameters = json.loads(template_parameters)
        )
        print("Publishing to RegisterThing topic...")
        future:Future = client.publish_register_thing(
            request = request,
            qos = mqtt.QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(fp.on_publish_RegisterThing)


    def __provision_by(self, connection:Connection, template_parameters:str) -> None:
        try:
            # Subscribe to necessary topics.
            # Note that is **is** important to wait for "accepted/rejected" subscriptions
            # to succeed before publishing the corresponding "request".
            client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(connection)
            self.__subscribe_and_pubrish_topics_by(client, template_parameters)
            print("Success")
            self.__disconnect(connection)
        except Exception as e:
            fp.error(e)


    def __subscribe_and_pubrish_topics_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict
    ) -> None:
        self.__subscribe_CreateKeysAndCertificate_topics_by(client)
        self.__subscribe_RegisterThing_topics_by(client)
        self.__publish_CreateKeysAndCertificate_topic_by(client)
        self.__publish_RegisterThing_topic_by(client, template_parameters)


    def provision_thing(
        self,
        cert:str,
        key:str,
        ca:str,
        template_parameters:str,
        client_id:str = str(uuid4()),
    ) -> str:
        connection:Connection = self.__create_connection_with(client_id, cert, key, ca)
        future:Future = connection.connect()

        # Wait for connection to be fully established.
        # Note that it's not necessary to wait, commands issued to the
        # mqtt_connection before its fully connected will simply be queued.
        # But this sample waits here so it's obvious when a connection
        # fails or succeeds.
        future.result()
        print("Connected!")
        self.__provision_by(connection, template_parameters)
        thing_name:str = self.__registerThingResponse.thing_name
        self.__is_sample_done.wait() # Wait for the sample to finish
        return thing_name


if __name__ == '__main__':
    config_path:str = 'config.json'
    with open(config_path) as config_file:
        config:dict = json.load(config_file)

    fleet:FleetProvisioning = FleetProvisioning(
        endpoint = config.get('endpoint'),
        template_name = config.get('template_name'),
    )

    folder:str = 'certs'
    claim:str = f'{folder}/claim.pem'

    thing_name:str = fleet.provision_thing(
        cert = f'{claim}.crt',
        key = f'{claim}.key',
        ca = f'{folder}/AmazonRootCA1.pem',
        template_parameters = config.get('template_parameters'),
        client_id = str(uuid4()),
    )
    print(f"Thing name: {thing_name}")