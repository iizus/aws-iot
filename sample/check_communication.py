from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


# from src.client.client import Client
from src.client.connection import Connection
from src.client.pubsub import check_communication, PubSub
from src.fleet_provisioning.provisioning import Provisioning, get_current_time


def main():
    check_communication()


def check_communications(times:int=3):
    # provisioning:Provisioning = Provisioning()
    pubsub:PubSub = PubSub()
    
    publisher_connection:Connection = pubsub.provisioning.provision_and_connect_thing(
        name = get_current_time()
    )
    subscriber_connection:Connection = pubsub.provisioning.provision_and_connect_thing(
        name = get_current_time()
    )

    for _ in range(times):
        pubsub.check_communication_between(publisher_connection, subscriber_connection)


if __name__ == '__main__':
    main()