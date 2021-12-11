# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

import argparse
from awscrt import auth, http, io, mqtt
from awsiot import iotidentity
from awsiot import mqtt_connection_builder
from concurrent.futures import Future
import sys
import threading
import time
import traceback
from uuid import uuid4
import json

# - Overview -
# This sample uses the AWS IoT Fleet Provisioning to provision device using either the keys
# or CSR
#
#
# - Instructions -
# This sample requires you to create a provisioning claim. See:
# https://docs.aws.amazon.com/iot/latest/developerguide/provision-wo-cert.html
#
# - Detail -
# On startup, the script subscribes to topics based on the request type of either CSR or Keys
# publishes the request to corresponding topic and calls RegisterThing.

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

io.init_logging(getattr(io.LogLevel, args.verbosity), 'stderr')
identity_client = None

createKeysAndCertificateResponse = None
createCertificateFromCsrResponse = None
registerThingResponse = None

class LockedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.disconnect_called = False

locked_data = LockedData()

# Function for gracefully quitting this sample
def exit(msg_or_exception, mqtt_connection):
    if isinstance(msg_or_exception, Exception):
        print("Exiting Sample due to exception.")
        traceback.print_exception(msg_or_exception.__class__, msg_or_exception, sys.exc_info()[2])
    else:
        print("Exiting Sample:", msg_or_exception)

    with locked_data.lock:
        if not locked_data.disconnect_called:
            print("Disconnecting...")
            locked_data.disconnect_called = True
            future = mqtt_connection.disconnect()
            future.add_done_callback(on_disconnected)

def on_disconnected(disconnect_future):
    # type: (Future) -> None
    print("Disconnected.")
    # Signal that sample is finished
    is_sample_done.set()

def on_publish_register_thing(future):
    # type: (Future) -> None
    try:
        future.result() # raises exception if publish failed
        print("Published RegisterThing request..")
    except Exception as e:
        print("Failed to publish RegisterThing request.")
        exit(e)

def on_publish_create_keys_and_certificate(future):
    # type: (Future) -> None
    try:
        future.result() # raises exception if publish failed
        print("Published CreateKeysAndCertificate request..")

    except Exception as e:
        print("Failed to publish CreateKeysAndCertificate request.")
        exit(e)

def on_publish_create_certificate_from_csr(future):
    # type: (Future) -> None
    try:
        future.result() # raises exception if publish failed
        print("Published CreateCertificateFromCsr request..")
    except Exception as e:
        print("Failed to publish CreateCertificateFromCsr request.")
        exit(e)

def createkeysandcertificate_execution_accepted(response):
    # type: (iotidentity.CreateKeysAndCertificateResponse) -> None
    try:
        global createKeysAndCertificateResponse
        createKeysAndCertificateResponse = response
        # print("Received a new message {}".format(createKeysAndCertificateResponse))
        print(f'Certificate ID: {createKeysAndCertificateResponse.certificate_id}')

        path = 'certs/client.pem'
        write_file(path=f'{path}.crt', content=createKeysAndCertificateResponse.certificate_pem)
        write_file(path=f'{path}.key', content=createKeysAndCertificateResponse.private_key)
        return
    except Exception as e:
        exit(e)


def write_file(path, content):
    with open(path, mode='w') as file:
        file.write(content)
        print(f'Saved {path}')
        print(content)


def createkeysandcertificate_execution_rejected(rejected):
    # type: (iotidentity.RejectedError) -> None
    exit("CreateKeysAndCertificate Request rejected with code:'{}' message:'{}' statuscode:'{}'".format(
        rejected.error_code, rejected.error_message, rejected.status_code))

def createcertificatefromcsr_execution_accepted(response):
    # type: (iotidentity.CreateCertificateFromCsrResponse) -> None
    try:
        global createCertificateFromCsrResponse
        createCertificateFromCsrResponse = response
        print("Received a new message {}".format(createCertificateFromCsrResponse))
        global certificateOwnershipToken
        certificateOwnershipToken = response.certificate_ownership_token
        return
    except Exception as e:
        exit(e)

def createcertificatefromcsr_execution_rejected(rejected):
    # type: (iotidentity.RejectedError) -> None
    exit("CreateCertificateFromCsr Request rejected with code:'{}' message:'{}' statuscode:'{}'".format(
        rejected.error_code, rejected.error_message, rejected.status_code))

def registerthing_execution_accepted(response):
    # type: (iotidentity.RegisterThingResponse) -> None
    try:
        global registerThingResponse
        registerThingResponse = response
        print("Received a new message {} ".format(registerThingResponse))
        return

    except Exception as e:
        exit(e)

def registerthing_execution_rejected(rejected):
    # type: (iotidentity.RejectedError) -> None
    exit("RegisterThing Request rejected with code:'{}' message:'{}' statuscode:'{}'".format(
        rejected.error_code, rejected.error_message, rejected.status_code))

# Callback when connection is accidentally lost.
def on_connection_interrupted(connection, error, **kwargs):
    print("Connection interrupted. error: {}".format(error))


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print("Connection resumed. return_code: {} session_present: {}".format(return_code, session_present))

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()

        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)

def on_resubscribe_complete(resubscribe_future):
    resubscribe_results = resubscribe_future.result()
    print("Resubscribe results: {}".format(resubscribe_results))

    for topic, qos in resubscribe_results['topics']:
        if qos is None:
            sys.exit("Server rejected resubscribe to topic: {}".format(topic))

def waitForCreateKeysAndCertificateResponse():
    # Wait for the response.
    loopCount = 0
    while loopCount < 10 and createKeysAndCertificateResponse is None:
        if createKeysAndCertificateResponse is not None:
            break
        print('Waiting... CreateKeysAndCertificateResponse: ' + json.dumps(createKeysAndCertificateResponse))
        loopCount += 1
        time.sleep(1)

def waitForCreateCertificateFromCsrResponse():
    # Wait for the response.
    loopCount = 0
    while loopCount < 10 and createCertificateFromCsrResponse is None:
        if createCertificateFromCsrResponse is not None:
            break
        print('Waiting...CreateCertificateFromCsrResponse: ' + json.dumps(createCertificateFromCsrResponse))
        loopCount += 1
        time.sleep(1)

def waitForRegisterThingResponse():
    # Wait for the response.
    loopCount = 0
    while loopCount < 20 and registerThingResponse is None:
        if registerThingResponse is not None:
            break
        loopCount += 1
        print('Waiting... RegisterThingResponse: ' + json.dumps(registerThingResponse))
        time.sleep(1)


def __create_connection(endpoint, cert, key, ca):
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
    print("Connecting to {args.endpoint} with client ID '{args.client_id}'...")
    return mqtt_connection


def __subscribe_CreateKeysAndCertificate_topics_by(client):
    request = iotidentity.CreateKeysAndCertificateSubscriptionRequest()
    __subscribe_CreateKeysAndCertificate_accepted_topic_by(client, request)
    __subscribe_CreateKeysAndCertificate_rejected_topic_by(client, request)


def __subscribe_CreateKeysAndCertificate_accepted_topic_by(client, request):
    print("Subscribing to CreateKeysAndCertificate Accepted topic...")
    future, _ = client.subscribe_to_create_keys_and_certificate_accepted(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = createkeysandcertificate_execution_accepted
    )
    # Wait for subscription to succeed
    future.result()


def __subscribe_CreateKeysAndCertificate_rejected_topic_by(client, request):
    print("Subscribing to CreateKeysAndCertificate Rejected topic...")
    future, _ = client.subscribe_to_create_keys_and_certificate_rejected(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = createkeysandcertificate_execution_rejected
    )
    # Wait for subscription to succeed
    future.result()


def __subscribe_RegisterThing_topics_by(client):
    request = iotidentity.RegisterThingSubscriptionRequest(
        template_name = args.templateName
    )
    __subscribe_RegisterThing_accepted_topic_by(client, request)
    __subscribe_RegisterThing_rejected_topic_by(client, request)


def __subscribe_RegisterThing_accepted_topic_by(client, request):
    print("Subscribing to CreateKeysAndCertificate Accepted topic...")
    future, _ = client.subscribe_to_register_thing_accepted(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = registerthing_execution_accepted
    )
    # Wait for subscription to succeed
    future.result()


def __subscribe_RegisterThing_rejected_topic_by(client, request):
    print("Subscribing to CreateKeysAndCertificate Rejected topic...")
    future, _ = client.subscribe_to_register_thing_rejected(
        request = request,
        qos = mqtt.QoS.AT_LEAST_ONCE,
        callback = registerthing_execution_rejected
    )
    # Wait for subscription to succeed
    future.result()


def __publish_CreateKeysAndCertificate_topic_by(client):
    print("Publishing to CreateKeysAndCertificate...")
    future = client.publish_create_keys_and_certificate(
        request = iotidentity.CreateKeysAndCertificateRequest(),
        qos = mqtt.QoS.AT_LEAST_ONCE
    )
    future.add_done_callback(on_publish_create_keys_and_certificate)

    waitForCreateKeysAndCertificateResponse()

    if createKeysAndCertificateResponse is None:
        raise Exception('CreateKeysAndCertificate API did not succeed')


def __publish_registerThing_topic_by(client):
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


def __provision_by(client, mqtt_connection):
    try:
        # Subscribe to necessary topics.
        # Note that is **is** important to wait for "accepted/rejected" subscriptions
        # to succeed before publishing the corresponding "request".
        __subscribe_CreateKeysAndCertificate_topics_by(client)
        __subscribe_RegisterThing_topics_by(client)
        __publish_CreateKeysAndCertificate_topic_by(client)
        __publish_registerThing_topic_by(client)
        exit("success", mqtt_connection)
    except Exception as e:
        exit(e, mqtt_connection)


def provision():
    mqtt_connection = __create_connection(
        endpoint = args.endpoint,
        cert = args.cert,
        key = args.key,
        ca = args.root_ca,
    )
    connected_future = mqtt_connection.connect()
    identity_client = iotidentity.IotIdentityClient(mqtt_connection)

    # Wait for connection to be fully established.
    # Note that it's not necessary to wait, commands issued to the
    # mqtt_connection before its fully connected will simply be queued.
    # But this sample waits here so it's obvious when a connection
    # fails or succeeds.
    connected_future.result()
    print("Connected!")
    __provision_by(identity_client, mqtt_connection)

    # Wait for the sample to finish
    is_sample_done.wait()


if __name__ == '__main__':
    provision()