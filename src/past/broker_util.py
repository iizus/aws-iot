from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)

from sys import exit
from concurrent.futures import Future
from awscrt import mqtt
from utils.util import load_json


def get_endpoint_from(config_path:str='endpoint.json', env_name:str='test', region:str='us-east-1') -> str:
    endpoints:dict = load_json(config_path)
    endpoint:str = endpoints.get(env_name)
    endpoint:str = f'{endpoint}-ats.iot.{region}.amazonaws.com'
    return endpoint


# Callback when an interrupted connection is re-established.
def on_connection_resumed(
    connection:mqtt.Connection,
    return_code,
    session_present
) -> None:
    print(f"Connection resumed. return code: {return_code} session present: {session_present}")

    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        print("Session did not persist. Resubscribing to existing topics...")
        resubscribe_future, _ = connection.resubscribe_existing_topics()
        # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
        # evaluate result with a callback instead.
        resubscribe_future.add_done_callback(__on_resubscribe_complete)


def __on_resubscribe_complete(resubscribe_future:Future):
    resubscribe_results = resubscribe_future.result()
    print(f"Resubscribe: {resubscribe_results}")
    topics = resubscribe_results.get('topics')
    for topic, QoS in topics:
        if QoS is None: exit(f"Server rejected resubscribe to {topic}")


# Callback when connection is accidentally lost.
def on_connection_interrupted(self, error) -> None:
    print(f"Connection interrupted. Error: {error}")



if __name__ == '__main__':
    from doctest import testmod
    testmod()