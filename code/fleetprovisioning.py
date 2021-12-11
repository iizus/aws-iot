import argparse
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


parser = argparse.ArgumentParser(description="Fleet Provisioning sample script.")
parser.add_argument('--endpoint', required=True, help="Your AWS IoT custom endpoint, not including a port. " +
                                                      "Ex: \"w6zbse3vjd5b4p-ats.iot.us-west-2.amazonaws.com\"")
parser.add_argument('--cert', help="File path to your client certificate, in PEM format")
parser.add_argument('--key', help="File path to your private key file, in PEM format")
parser.add_argument('--root-ca', help="File path to root certificate authority, in PEM format. " +
                                      "Necessary if MQTT server uses a certificate that's not already in " +
                                      "your trust store")
parser.add_argument('--client-id', default="test-" + str(uuid4()), help="Client ID for MQTT connection.")
parser.add_argument('--use-websocket', default=False, action='store_true',
                    help="To use a websocket instead of raw mqtt. If you " +
                         "specify this option you must specify a region for signing.")
parser.add_argument('--signing-region', default='us-east-1', help="If you specify --use-web-socket, this " +
                                                                  "is the region that will be used for computing the Sigv4 signature")
parser.add_argument('--proxy-host', help="Hostname of proxy to connect to.")
parser.add_argument('--proxy-port', type=int, default=8080, help="Port of proxy to connect to.")
parser.add_argument('--verbosity', choices=[x.name for x in io.LogLevel], default=io.LogLevel.NoLogs.name,
                    help='Logging level')
parser.add_argument("--csr", help="File path to your client CSR in PEM format")
parser.add_argument("--templateName", help="Template name")
parser.add_argument("--templateParameters", help="Values for Template Parameters")

# Using globals to simplify sample code
is_sample_done = threading.Event()
args = parser.parse_args()

__log_level = getattr(io.LogLevel, args.verbosity)
io.init_logging(__log_level, 'stderr')

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
        print(f'Certificate ID: {response.certificate_id}')
        __save_certs_based_on(response)
        return
    except Exception as e:
        __error(e)


def __save_certs_based_on(response: iotidentity.CreateKeysAndCertificateResponse) -> None:
    path = 'certs/client.pem'
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
        print('Waiting... registerThingResponse: ' + json.dumps(registerThingResponse))
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


def __create_connection(endpoint: str, cert: str, key: str, ca: str) -> Connection:
    # Spin up resources
    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint = endpoint,
        cert_filepath = cert,
        pri_key_filepath = key,
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver),
        ca_filepath = ca,
        client_id = str(uuid4()),
        on_connection_interrupted = on_connection_interrupted,
        on_connection_resumed = on_connection_resumed,
        clean_session = False,
        keep_alive_secs = 30,
        http_proxy_options = None,
    )
    print(f"Connecting to {args.endpoint} with client ID '{args.client_id}'...")
    return mqtt_connection


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
    print("Subscribing to CreateKeysAndCertificate Accepted topic...")
    future, _ = client.subscribe_to_create_keys_and_certificate_accepted(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = createkeysandcertificate_execution_accepted
    )
    # Wait for subscription to succeed
    future.result()


def __subscribe_CreateKeysAndCertificate_rejected_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.CreateKeysAndCertificateSubscriptionRequest
) -> None:
    print("Subscribing to CreateKeysAndCertificate Rejected topic...")
    future, _ = client.subscribe_to_create_keys_and_certificate_rejected(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = createkeysandcertificate_execution_rejected
    )
    # Wait for subscription to succeed
    future.result()


def __subscribe_RegisterThing_topics_by(client: iotidentity.IotIdentityClient) -> None:
    request = iotidentity.RegisterThingSubscriptionRequest(
        template_name = args.templateName
    )
    __subscribe_RegisterThing_accepted_topic_by(client, request)
    __subscribe_RegisterThing_rejected_topic_by(client, request)


def __subscribe_RegisterThing_accepted_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.RegisterThingRequest
) -> None:
    print("Subscribing to CreateKeysAndCertificate Accepted topic...")
    future, _ = client.subscribe_to_register_thing_accepted(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = registerthing_execution_accepted
    )
    # Wait for subscription to succeed
    future.result()


def __subscribe_RegisterThing_rejected_topic_by(
    client: iotidentity.IotIdentityClient,
    request: iotidentity.RegisterThingRequest
) -> None:
    print("Subscribing to CreateKeysAndCertificate Rejected topic...")
    future, _ = client.subscribe_to_register_thing_rejected(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = registerthing_execution_rejected
    )
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


def __publish_registerThing_topic_by(client: iotidentity.IotIdentityClient) -> None:
    request = iotidentity.RegisterThingRequest(
        template_name = args.templateName,
        certificate_ownership_token = createKeysAndCertificateResponse.certificate_ownership_token,
        parameters = json.loads(args.templateParameters)
    )
    print("Publishing to RegisterThing topic...")
    future = client.publish_register_thing(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE
    )
    future.add_done_callback(on_publish_register_thing)
    waitForRegisterThingResponse()
    # __wait_for('registerThingResponse', registerThingResponse)


def __provision_by(connection: Connection) -> None:
    try:
        # Subscribe to necessary topics.
        # Note that is **is** important to wait for "accepted/rejected" subscriptions
        # to succeed before publishing the corresponding "request".
        client = iotidentity.IotIdentityClient(connection)
        __subscribe_and_pubrish_topics_by(client)
        print("Success")
        __disconnect(connection)
    except Exception as e:
        __error(e)


def __subscribe_and_pubrish_topics_by(client: iotidentity.IotIdentityClient) -> None:
    __subscribe_CreateKeysAndCertificate_topics_by(client)
    __subscribe_RegisterThing_topics_by(client)
    __publish_CreateKeysAndCertificate_topic_by(client)
    __publish_registerThing_topic_by(client)


def provision():
    mqtt_connection = __create_connection(
        endpoint = args.endpoint,
        cert = args.cert,
        key = args.key,
        ca = args.root_ca,
    )
    connected_future = mqtt_connection.connect()

    # Wait for connection to be fully established.
    # Note that it's not necessary to wait, commands issued to the
    # mqtt_connection before its fully connected will simply be queued.
    # But this sample waits here so it's obvious when a connection
    # fails or succeeds.
    connected_future.result()
    print("Connected!")
    __provision_by(mqtt_connection)

    # Wait for the sample to finish
    is_sample_done.wait()


if __name__ == '__main__':
    provision()