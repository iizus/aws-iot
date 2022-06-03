import os
from sys import exc_info
from traceback import print_exception
from awsiot import iotidentity
from concurrent.futures import Future
from time import sleep
from shutil import rmtree
from src.utils.util import print_log


def on_publish_CreateKeysAndCertificate(future:Future) -> None:
    __callback('CreateKeysAndCertificate', future)


def on_publish_RegisterThing(future:Future) -> None:
    __callback('RegisterThing', future)


def __callback(api:str, future:Future) -> None:
    try:
        future.result() # raises exception if publish failed
        print(f"Published {api} request")
    except Exception as e:
        print(f"Failed to publish {api} request")
        error(e)


def save_certs_in(dir:str, response:iotidentity.CreateKeysAndCertificateResponse, thing_name:str) -> None:
    path:str = __get_certs_path_based_on(thing_name, response.certificate_id, dir)
    __save_certs_at(path, response)


def __get_certs_path_based_on(thing_name:str, certificate_id:str, dir:str='certs/fleet_provisioning/individual') -> str:
    folder:str = f'{dir}/{thing_name}'
    dir_path:str = __create(folder)
    path:str = f"{dir_path}/{certificate_id}.pem"
    return path


def __save_certs_at(path:str, response:iotidentity.CreateKeysAndCertificateResponse) -> None:
    __save_file(path=f'{path}.crt', content=response.certificate_pem)
    __save_file(path=f'{path}.key', content=response.private_key)


def __create(folder:str) -> str:
    if os.path.exists(folder): rmtree(folder)
    os.makedirs(folder)
    return folder


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
        exc_info()[2],
    )