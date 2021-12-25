import sys
import threading
import traceback
from awsiot import iotidentity
from concurrent.futures import Future


class LockedData:
    def __init__(self):
        self.lock: threading.Lock = threading.Lock()
        self.disconnect_called: bool = False


def callback(api: str, future: Future) -> None:
    try:
        future.result() # raises exception if publish failed
        print(f"Published {api} request")
    except Exception as e:
        print(f"Failed to publish {api} request")
        error(e)


def save_certs_based_on(
    response: iotidentity.CreateKeysAndCertificateResponse,
    folder: str = 'certs'
) -> None:
    path: str = f"{folder}/client.pem"
    __save_file(path=f'{path}.crt', content=response.certificate_pem)
    __save_file(path=f'{path}.key', content=response.private_key)


def __save_file(path: str, content: str) -> None:
    with open(path, mode='w') as file:
        file.write(content)
        print(f'Saved {path}')


def print_rejected(api: str, response: iotidentity.ErrorResponse) -> None:
    error(f"{api} request rejected with code: {response.error_code} message: {response.error_message} status code: {response.status_code}")


# Function for gracefully quitting this sample
def error(msg_or_exception: Exception) -> None:
    print("Exiting Sample due to exception")
    traceback.print_exception(
        msg_or_exception.__class__,
        msg_or_exception,
        sys.exc_info()[2]
    )