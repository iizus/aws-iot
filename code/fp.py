import sys
from threading import Lock
from traceback import print_exception
from awsiot import iotidentity
from concurrent.futures import Future
from time import sleep
from awscrt.mqtt import Connection, ConnectReturnCode


class LockedData:
    def __init__(self):
        self.lock:Lock = Lock()
        self.disconnect_called:bool = False


def on_publish_CreateKeysAndCertificate(future:Future) -> None:
    __callback('CreateKeysAndCertificate', future)


def on_publish_RegisterThing(future:Future) -> None:
    __callback('RegisterThing', future)


# Callback when an interrupted connection is re-established.
def on_connection_resumed(
    connection:Connection,
    return_code,
    session_present
) -> None:
    print(f"Connection resumed. return code: {return_code} session present: {session_present}")

    if return_code == ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(on_resubscribe_complete)


def on_resubscribe_complete(future:Future) -> None:
    results = future.result()
    print(f"Resubscribe results: {results}")
    for topic, qos in results.get('topics'):
        if qos is None: sys.error(f"Server rejected resubscribe to topic: {topic}")


# Callback when connection is accidentally lost.
def on_connection_interrupted(error) -> None:
    print(f"Connection interrupted. Error: {error}")


def __callback(api:str, future:Future) -> None:
    try:
        future.result() # raises exception if publish failed
        print(f"Published {api} request")
    except Exception as e:
        print(f"Failed to publish {api} request")
        error(e)


def save_certs_based_on(
    response:iotidentity.CreateKeysAndCertificateResponse,
    folder:str = 'certs'
) -> None:
    path:str = f"{folder}/client.pem"
    __save_file(path=f'{path}.crt', content=response.certificate_pem)
    __save_file(path=f'{path}.key', content=response.private_key)


def __save_file(path:str, content:str) -> None:
    with open(path, mode='w') as file:
        file.write(content)
        print(f'Saved {path}')


def print_rejected(api:str, response:iotidentity.ErrorResponse) -> None:
    error(f"{api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")


# Function for gracefully quitting this sample
def error(msg_or_exception:Exception) -> None:
    print("Exiting Sample due to exception")
    print_exception(
        msg_or_exception.__class__,
        msg_or_exception,
        sys.exc_info()[2],
    )


def wait_for(response:str) -> None:
    print(f'Waiting... {response}')
    sleep(1)