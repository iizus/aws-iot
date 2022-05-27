from account import Account
# from broker import Broker
# from project import Project
# from client import Client
# from connection import Connection
# from topic import Topic


class Topic:
    def __init__(self, name:str='test/test') -> None:
        pass

    def publish(self, message:dict) -> dict:
        return response

    def subscribe(self, callback) -> dict:
        return response

    def unsubscribe(self) -> dict:
        return response


class Connection:
    def __init__(self) -> None:
        pass

    def use_topic(self, name:str='test/test') -> Topic:
        return Topic(name)

    def disconnect(self) -> dict:
        return response


class Client:
    def __init__(self) -> None:
        pass

    def connect(self) -> Connection:
        return Connection()


class Project:
    def __init__(self, endpoint:str, name:str='test') -> None:
        pass

    def create_client_using(self, certs_dir:str='test') -> Client:
        return Client()


# def provision_thing(self, name:str) -> Client:
#     fp:Project = self.create_project(name='fleet_provisioning')
#     claim:Client = fp.create_client_using(certs_dir='claim')
#     provisioning_connection:Connection = claim.connect()
#     thing_name:str = provisioning_connection.provision_thing(name)
#     client:Project = self.create_project(name=thing_name)
#     individual:Client = client.create_client_using(certs_dir=f'individual/{thing_name}')
#     return individual


test:Account = Account(name='test')
burner:Account = Account(name='burner')

# virginia:Region = test.use(region='us-east-1')
# tokyo:Region = test.use(region='ap-northeast-1')

# client1:Client = virginia.provision_thing(name='client1')

# client1_connection:Connection = client1.connect()

# topic_aaa:Topic = client1_connection.use_topic(name='aaa')
# topic_bbb:Topic = client1_connection.use_topic(name='bbb')

# response:dict = topic_aaa.pub(message)
# response:dict = topic_aaa.sub(callback)
# response:dict = topic_aaa.unsub()

# response:dict = client1_connection.disconnect()




# if __name__ == '__main__':
#     from doctest import testmod
#     testmod()