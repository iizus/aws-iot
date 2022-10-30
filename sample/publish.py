from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.account import PubSub, get_endpoint

def main():
    pubsub:PubSub = PubSub(endpoint=get_endpoint())
    pubsub.publish()

if __name__ == '__main__':
    main()