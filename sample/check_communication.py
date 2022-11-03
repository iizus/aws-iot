from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.client import Client
from src.client.pubsub import check_communication, PubSub
from src.fleet_provisioning.provisioning import Provisioning


def main():
    check_communication()


def check_communications(times:int=3):
    pubsub:PubSub = PubSub()
    provisioning:Provisioning = Provisioning()
    
    publisher:Client = provisioning.provision_thing()
    subscriber:Client = provisioning.provision_thing()

    for _ in range(times):
        pubsub.check_communication_between(publisher, subscriber)


if __name__ == '__main__':
    main()