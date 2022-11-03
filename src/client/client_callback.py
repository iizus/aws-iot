from src.utils import util
from awscrt import mqtt
from typing import List
from concurrent.futures import Future


# Callback when an interrupted connection is re-established.
def on_connection_resumed(connection:mqtt.Connection, return_code:int, session_present:bool) -> None:
    util.print_log(
        subject = connection.client_id,
        verb = 'Resumed',
        message = f"connection with {connection.host_name}, Return code: {return_code} and Session present: {session_present}"
    )
    if return_code == mqtt.ConnectReturnCode.ACCEPTED and not session_present:
        packet_id:int = __resubscribe(connection)
        

def __resubscribe(connection:mqtt.Connection) -> int:
    client_id:str = connection.client_id
    endpoint:str = connection.host_name
    print("Session did not persist. Resubscribing to existing topics...")
    util.print_log(subject=client_id, verb='Resubscribing...', message=f"Endpoint: {endpoint}")
    resubscribe_future, packet_id = connection.resubscribe_existing_topics()
    # Cannot synchronously wait for resubscribe result because we're on the connection's event-loop thread,
    # evaluate result with a callback instead.
    resubscribe_future.add_done_callback(__on_resubscribe_complete)
    util.print_log(
        subject = client_id,
        verb = 'Resubscribed',
        message = f"Endpoint: {endpoint} Packet ID: {packet_id}"
    )
    return packet_id


def __on_resubscribe_complete(resubscribe_future:Future) -> None:
    resubscribe_results = resubscribe_future.result()
    topics:List[str] = resubscribe_results.get('topics')
    packet_id:int = resubscribe_results.get('packet_id')
    print(f"Resubscribe: {resubscribe_results}")
    for topic, QoS in topics:
        if QoS is None: exit(f"Server rejected resubscribe to {topic}")


# Callback when connection is accidentally lost.
def on_connection_interrupted(error) -> None:
    print(f"Connection interrupted. Error: {error}")