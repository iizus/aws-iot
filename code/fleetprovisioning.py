from multiprocessing.connection import Connection
from awscrt import io, mqtt
from awsiot import iotidentity, mqtt_connection_builder
from concurrent.futures import Future
import sys
import threading
import time
from uuid import uuid4
import json
import fp


# Using globals to simplify sample code
is_sample_done = threading.Event()
createKeysAndCertificateResponse = None
createCertificateFromCsrResponse = None
registerThingResponse = None


def __disconnect(mqtt_connection):
    locked_data: fp.LockedData = fp.LockedData()
    with locked_data.lock:
        if not locked_data.disconnect_called:
            print("Disconnecting...")
            locked_data.disconnect_called = True
            future: Future = mqtt_connection.disconnect()
            future.add_done_callback(on_disconnected)

    
def on_disconnected(future: Future) -> None:
    print("Disconnected")
    # Signal that sample is finished
    is_sample_done.set()


def on_publish_RegisterThing(future: Future) -> None:
    fp.callback('RegisterThing', future)


def on_publish_CreateKeysAndCertificate(future: Future) -> None:
    fp.callback('CreateKeysAndCertificate', future)


def on_CreateKeysAndCertificate_accepted(response: iotidentity.CreateKeysAndCertificateResponse) -> None:
    try:
        global createKeysAndCertificateResponse
        createKeysAndCertificateResponse = response
        print(f"Certificate ID: {response.certificate_id}")
        fp.save_certs_based_on(response)
        return
    except Exception as e:
        fp.error(e)


def on_CreateKeysAndCertificate_rejected(
    response: iotidentity.ErrorResponse
) -> None:
    fp.print_rejected('CreateKeysAndCertificate', response)


def on_RegisterThing_accepted(response: iotidentity.RegisterThingResponse) -> None:
    try:
        global registerThingResponse
        registerThingResponse = response
        print(f"Received a new message {registerThingResponse}")
        return
    except Exception as e:
        fp.error(e)


def on_RegisterThing_rejected(response: iotidentity.ErrorResponse) -> None:
    fp.print_rejected('RegisterThing', response)


# Callback when connection is accidentally lost.
def on_connection_interrupted(connection: Connection, error, **kwargs) -> None:
    print(f"Connection interrupted. Error: {error}")


# Callback when an interrupted connection is re-established.
def on_connection_resumed(
    connection: Connection,
    return_code,
    session_present,
    **kwargs
) -> None:
    print(f"Connection resumed. return code: {return_code} session present: {session_present}")

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(future: Future) -> None:
    results = future.result()
    print(f"Resubscribe results: {results}")
    for topic, qos in results.get('topics'):
        if qos is None: sys.error(f"Server rejected resubscribe to topic: {topic}")


def waitForCreateKeysAndCertificateResponse():
    # Wait for the response.
    loopCount: int = 0
    while loopCount < 10 and createKeysAndCertificateResponse is None:
        if createKeysAndCertificateResponse is not None:
            break
        message = json.dumps(createKeysAndCertificateResponse)
        print(f"Waiting... CreateKeysAndCertificateResponse: {message}")
        loopCount += 1
        time.sleep(1)


def waitForRegisterThingResponse():
    # Wait for the response.
    loopCount: int = 0
    while loopCount < 20 and registerThingResponse is None:
        if registerThingResponse is not None:
            break
        loopCount += 1
        message = json.dumps(registerThingResponse)
        print(f"Waiting... registerThingResponse: {message}")
        time.sleep(1)


# def __wait_for(api, response):
#     # Wait for the response.
#     loopCount = 0
#     while loopCount < 10 and response is None:
#         if response is not None:
#             break
#         loopCount += 1
#         message = json.dumps(response)
#         print(f'Waiting {api}... : {message}')
#         time.sleep(1)


def __create_connection(endpoint: str, cert: str, key: str, ca: str, client_id: str) -> Connection:
    # Spin up resources
    event_loop_group: io.EventLoopGroup = io.EventLoopGroup(1)
    host_resolver: io.DefaultHostResolver = io.DefaultHostResolver(event_loop_group)

    connection: Connection = mqtt_connection_builder.mtls_from_path(
        endpoint = endpoint,
        cert_filepath = cert,
        pri_key_filepath = key,
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver),
        ca_filepath = ca,
        client_id = client_id,
        on_connection_interrupted = on_connection_interrupted,
        on_connection_resumed = on_connection_resumed,
        clean_session = False,
        keep_alive_secs = 30,
        http_proxy_options = None,
    )
    print(f"Connecting to {endpoint} with client ID '{client_id}'...")
    return connection


def __subscribe_CreateKeysAndCertificate_topics_by(
    client: iotidentity.IotIdentityClient
) -> None:
    request: iotidentity.CreateKeysAndCertificateSubscriptionRequest = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
    __subscribe_CreateKeysAndCertificate_accepted_topic_by(client, request)
    __subscribe_CreateKeysAndCertificate_rejected_topic_by(client, request)


def __subscribe_CreateKeysAndCertificate_accepted_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.CreateKeysAndCertificateSubscriptionRequest
) -> None:
    future, topic = client.subscribe_to_create_keys_and_certificate_accepted(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = on_CreateKeysAndCertificate_accepted
    )
    print(f"Subscribed {topic}")
    # Wait for subscription to succeed
    future.result()


def __subscribe_CreateKeysAndCertificate_rejected_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.CreateKeysAndCertificateSubscriptionRequest
) -> None:
    future, topic = client.subscribe_to_create_keys_and_certificate_rejected(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = on_CreateKeysAndCertificate_rejected
    )
    print(f"Subscribed {topic}")
    # Wait for subscription to succeed
    future.result()


def __subscribe_RegisterThing_topics_by(
    client: iotidentity.IotIdentityClient,
    template_name: str
) -> None:
    request: iotidentity.RegisterThingSubscriptionRequest = iotidentity.RegisterThingSubscriptionRequest(
        template_name = template_name
    )
    __subscribe_RegisterThing_accepted_topic_by(client, request)
    __subscribe_RegisterThing_rejected_topic_by(client, request)


def __subscribe_RegisterThing_accepted_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.RegisterThingRequest
) -> None:
    future, topic = client.subscribe_to_register_thing_accepted(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = on_RegisterThing_accepted
    )
    print(f"Subscribed {topic}")
    # Wait for subscription to succeed
    future.result()


def __subscribe_RegisterThing_rejected_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.RegisterThingRequest
) -> None:
    # print("Subscribing to CreateKeysAndCertificate Rejected topic...")
    future, topic = client.subscribe_to_register_thing_rejected(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = on_RegisterThing_rejected
    )
    print(f"Subscribed {topic}")
    # Wait for subscription to succeed
    future.result()


def __publish_CreateKeysAndCertificate_topic_by(
    client: iotidentity.IotIdentityClient
) -> None:
    print("Publishing to CreateKeysAndCertificate...")
    future: Future = client.publish_create_keys_and_certificate(
        request = iotidentity.CreateKeysAndCertificateRequest(),
        qos = mqtt.QoS.AT_LEAST_ONCE
    )
    future.add_done_callback(on_publish_CreateKeysAndCertificate)
    waitForCreateKeysAndCertificateResponse()
    # __wait_for('createKeysAndCertificateResponse', createKeysAndCertificateResponse)
    if createKeysAndCertificateResponse is None:
        raise Exception('CreateKeysAndCertificate API did not succeed')


def __publish_RegisterThing_topic_by(
    client: iotidentity.IotIdentityClient,
    template_name: str,
    template_parameters: dict
) -> None:
    request = iotidentity.RegisterThingRequest(
        template_name = template_name,
        certificate_ownership_token = createKeysAndCertificateResponse.certificate_ownership_token,
        parameters = json.loads(template_parameters)
    )
    print("Publishing to RegisterThing topic...")
    future = client.publish_register_thing(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE
    )
    future.add_done_callback(on_publish_RegisterThing)
    waitForRegisterThingResponse()
    # __wait_for('registerThingResponse', registerThingResponse)


def __provision_by(connection: Connection, template_name: str, template_parameters: str) -> None:
    try:
        # Subscribe to necessary topics.
        # Note that is **is** important to wait for "accepted/rejected" subscriptions
        # to succeed before publishing the corresponding "request".
        client: iotidentity.IotIdentityClient = iotidentity.IotIdentityClient(connection)
        __subscribe_and_pubrish_topics_by(client, template_name, template_parameters)
        print("Success")
        __disconnect(connection)
    except Exception as e:
        fp.error(e)


def __subscribe_and_pubrish_topics_by(
    client: iotidentity.IotIdentityClient,
    template_name: str,
    template_parameters: dict
) -> None:
    __subscribe_CreateKeysAndCertificate_topics_by(client)
    __subscribe_RegisterThing_topics_by(client, template_name)
    __publish_CreateKeysAndCertificate_topic_by(client)
    __publish_RegisterThing_topic_by(client, template_name, template_parameters)


def provision_thing(
    endpoint: str,
    cert: str,
    key: str,
    ca: str,
    template_name: str,
    template_parameters: str
) -> str:
    connection: Connection = __create_connection(endpoint, cert, key, ca, client_id=str(uuid4()))
    future: Future = connection.connect()

    # Wait for connection to be fully established.
    # Note that it's not necessary to wait, commands issued to the
    # mqtt_connection before its fully connected will simply be queued.
    # But this sample waits here so it's obvious when a connection
    # fails or succeeds.
    future.result()
    print("Connected!")
    __provision_by(connection, template_name, template_parameters)
    thing_name: str = registerThingResponse.thing_name

    # Wait for the sample to finish
    is_sample_done.wait()
    return thing_name


if __name__ == '__main__':
    config_path: str = 'config.json'
    with open(config_path) as config_file:
        config: dict = json.load(config_file)

    folder: str = 'certs'
    claim: str = f'{folder}/claim.pem'

    thing_name: str = provision_thing(
        endpoint = config.get('endpoint'),
        cert = f'{claim}.crt',
        key = f'{claim}.key',
        ca = f'{folder}/AmazonRootCA1.pem',
        template_name = config.get('template_name'),
        template_parameters = config.get('template_parameters'),
    )
    print(f"Thing name: {thing_name}")