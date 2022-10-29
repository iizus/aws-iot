from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.topic import Topic
from src.client.account import Endpoint, get_endpoint_of

def publish(topic:Topic) -> None:
    topic.publish({'from': topic.client_id})

def check_publishing_to(endpoint:Endpoint) -> None:
    fp:Endpoint = endpoint.set_FP()
    endpoint.excute_callback_on(
        client = fp.provision_thing(),
        callback = publish
    )

def main():
    isengard_virginia:Endpoint = get_endpoint_of()
    check_publishing_to(isengard_virginia)


if __name__ == '__main__':
    main()