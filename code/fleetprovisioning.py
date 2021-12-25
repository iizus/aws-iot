from multiprocessing.connection import Connection
from awscrt import io, mqtt
from awsiot import iotidentity, mqtt_connection_builder
from concurrent.futures import Future
import sys
import threading
import time
import traceback
from uuid import uuid4
import json


# Using globals to simplify sample code
is_sample_done = threading.Event()
createKeysAndCertificateResponse = None
createCertificateFromCsrResponse = None
registerThingResponse = None


class LockedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.disconnect_called = False


def __disconnect(mqtt_connection):
    locked_data = LockedData()
    with locked_data.lock:
        if not locked_data.disconnect_called:
            print("Disconnecting...")
            locked_data.disconnect_called = True
            future = mqtt_connection.disconnect()
            future.add_done_callback(on_disconnected)


# Function for gracefully quitting this sample
def __error(msg_or_exception):
    print("Exiting Sample due to exception")
    traceback.print_exception(
        msg_or_exception.__class__,
        msg_or_exception,
        sys.exc_info()[2]
    )

    
def on_disconnected(future: Future) -> None:
    print("Disconnected")
    # Signal that sample is finished
    is_sample_done.set()


def on_publish_register_thing(future: Future) -> None:
    __callback('RegisterThing', future)


def on_publish_create_keys_and_certificate(future: Future) -> None:
    __callback('CreateKeysAndCertificate', future)


def __callback(api: str, future: Future) -> None:
    try:
        future.result() # raises exception if publish failed
        print(f"Published {api} request")
    except Exception as e:
        print(f"Failed to publish {api} request")
        __error(e)


def createkeysandcertificate_execution_accepted(response: iotidentity.CreateKeysAndCertificateResponse) -> None:
    try:
        global createKeysAndCertificateResponse
        createKeysAndCertificateResponse = response
        print(f"Certificate ID: {response.certificate_id}")
        __save_certs_based_on(response)
        return
    except Exception as e:
        __error(e)


def __save_certs_based_on(
    response: iotidentity.CreateKeysAndCertificateResponse,
    folder: str = 'certs'
) -> None:
    path = f"{folder}/client.pem"
    __save_file(path=f'{path}.crt', content=response.certificate_pem)
    __save_file(path=f'{path}.key', content=response.private_key)


def __save_file(path: str, content: str) -> None:
    with open(path, mode='w') as file:
        file.write(content)
        print(f'Saved {path}')


def createkeysandcertificate_execution_rejected(
    response: iotidentity.ErrorResponse
) -> None:
    __print_rejected('CreateKeysAndCertificate', response)


def registerthing_execution_accepted(response: iotidentity.RegisterThingResponse) -> None:
    try:
        global registerThingResponse
        registerThingResponse = response
        print(f"Received a new message {registerThingResponse}")
        return
    except Exception as e:
        __error(e)


def registerthing_execution_rejected(response: iotidentity.ErrorResponse) -> None:
    __print_rejected('RegisterThing', response)


def __print_rejected(api: str, response: iotidentity.ErrorResponse) -> None:
    __error(f"{api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")


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
        if qos is None: sys.__error(f"Server rejected resubscribe to topic: {topic}")


def waitForCreateKeysAndCertificateResponse():
    # Wait for the response.
    loopCount = 0
    while loopCount < 10 and createKeysAndCertificateResponse is None:
        if createKeysAndCertificateResponse is not None:
            break
        print('Waiting... CreateKeysAndCertificateResponse: ' + json.dumps(createKeysAndCertificateResponse))
        loopCount += 1
        time.sleep(1)


def waitForRegisterThingResponse():
    # Wait for the response.
    loopCount = 0
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

    connection = mqtt_connection_builder.mtls_from_path(
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
    request = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
    __subscribe_CreateKeysAndCertificate_accepted_topic_by(client, request)
    __subscribe_CreateKeysAndCertificate_rejected_topic_by(client, request)


def __subscribe_CreateKeysAndCertificate_accepted_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.CreateKeysAndCertificateSubscriptionRequest
) -> None:
    future, topic = client.subscribe_to_create_keys_and_certificate_accepted(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = createkeysandcertificate_execution_accepted
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
        callback = createkeysandcertificate_execution_rejected
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
        callback = registerthing_execution_accepted
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
        callback = registerthing_execution_rejected
    )
    print(f"Subscribed {topic}")
    # Wait for subscription to succeed
    future.result()


def __publish_CreateKeysAndCertificate_topic_by(
    client: iotidentity.IotIdentityClient
) -> None:
    print("Publishing to CreateKeysAndCertificate...")
    future = client.publish_create_keys_and_certificate(
        request = iotidentity.CreateKeysAndCertificateRequest(),
        qos = mqtt.QoS.AT_LEAST_ONCE
    )
    future.add_done_callback(on_publish_create_keys_and_certificate)
    waitForCreateKeysAndCertificateResponse()
    # __wait_for('createKeysAndCertificateResponse', createKeysAndCertificateResponse)
    if createKeysAndCertificateResponse is None:
        raise Exception('CreateKeysAndCertificate API did not succeed')


def __publish_registerThing_topic_by(
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
    future.add_done_callback(on_publish_register_thing)
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
        __error(e)


def __subscribe_and_pubrish_topics_by(
    client: iotidentity.IotIdentityClient,
    template_name: str,
    template_parameters: dict
) -> None:
    __subscribe_CreateKeysAndCertificate_topics_by(client)
    __subscribe_RegisterThing_topics_by(client, template_name)
    __publish_CreateKeysAndCertificate_topic_by(client)
    __publish_registerThing_topic_by(client, template_name, template_parameters)


def provision_thing(
    endpoint: str,
    cert: str,
    key: str,
    ca: str,
    template_name: str,
    template_parameters: str
) -> str:
    connection: Connection = __create_connection(endpoint, cert, key, ca, client_id=str(uuid4()))
    future = connection.connect()

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