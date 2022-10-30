from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)


from src.client.pubsub import check_communication

def main():
    check_communication()

if __name__ == '__main__':
    main()