from awscrt import io, mqtt
from awsiot import iotidentity, mqtt_connection_builder
from concurrent.futures import Future
from threading import Event
from uuid import uuid4
import fp
from connection import MQTT


class FleetProvisioning:
    def __init__(self, template_name:str) -> None:
        self.__template_name:str = template_name
        self.__is_sample_done:Event = Event()
        self.__createKeysAndCertificateResponse:iotidentity.CreateKeysAndCertificateResponse = None
        self.__registerThingResponse:iotidentity.RegisterThingResponse = None


    def __disconnect(self, mqtt_connection:mqtt.Connection):
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


    def __create_keys_and_certificate_by(
        self,
        client:iotidentity.IotIdentityClient
    ) -> None:
        self.__publish_CreateKeysAndCertificate_topic_by(client)
        loop_count:int = 0
        while loop_count < 10 and self.__createKeysAndCertificateResponse is None:
            if self.__createKeysAndCertificateResponse is not None: break
            fp.wait_for('createKeysAndCertificateResponse')
            loop_count += 1

        if self.__createKeysAndCertificateResponse is None:
            raise Exception('CreateKeysAndCertificate API did not succeed')


    def __publish_CreateKeysAndCertificate_topic_by(
        self,
        client:iotidentity.IotIdentityClient
    ) -> None:
        print("Publishing to CreateKeysAndCertificate...")
        future:Future = client.publish_create_keys_and_certificate(
            request = iotidentity.CreateKeysAndCertificateRequest(),
            qos = mqtt.QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(fp.on_publish_CreateKeysAndCertificate)


    def __register_thing_by(
        self,
        client:iotidentity.IotIdentityClient,
        template_parameters:dict
    ) -> None:
        self.__publish_RegisterThing_topic_by(client, template_parameters)
        loop_count:int = 0
        while loop_count < 10 and self.__registerThingResponse is None:
            if self.__registerThingResponse is not None: break
            fp.wait_for('registerThingResponse')
            loop_count += 1


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
        print("Publishing to RegisterThing topic...")
        future:Future = client.publish_register_thing(
            request = request,
            qos = mqtt.QoS.AT_LEAST_ONCE
        )
        future.add_done_callback(fp.on_publish_RegisterThing)


    def __provision_by(self, connection:mqtt.Connection, template_parameters:str) -> None:
        try:
            # Subscribe to necessary topics.
            # Note that is **is** important to wait for "accepted/rejected" subscriptions
            # to succeed before publishing the corresponding "request".
            client:iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(connection)
            self.__subscribe_and_pubrish_topics_by(client, template_parameters)
            print("Success fleet provisioning")
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
        self.__create_keys_and_certificate_by(client)
        self.__register_thing_by(client, template_parameters)


    def provision_thing_by(
        self,
        connection:mqtt.Connection,
        template_parameters:str,
    ) -> str:
        self.__provision_by(connection, template_parameters)
        thing_name:str = self.__registerThingResponse.thing_name
        self.__is_sample_done.wait() # Wait for the sample to finish
        return thing_name


if __name__ == '__main__':
    config_path:str = 'config.json'
    with open(config_path) as config_file:
        from json import load
        config:dict = load(config_file)

    fleet:FleetProvisioning = FleetProvisioning(template_name = config.get('template_name'))

    folder:str = 'certs'
    claim:str = f'{folder}/claim.pem'
    device_ID = str(uuid4())
    print(f"Device ID: {device_ID}")

    mqtt_connection = MQTT(endpoint=config.get('endpoint'))
    connection = mqtt_connection.connect_with(
        client_id = device_ID,
        cert = f'{claim}.crt',
        key = f'{claim}.key',
        ca = f'{folder}/AmazonRootCA1.pem',
    )
    thing_name:str = fleet.provision_thing_by(
        connection = connection,
        template_parameters = {"DeviceID": device_ID},
    )