# from broker import Broker
# from pubsub.pubsub import Client
# from awscrt import mqtt


# def connect(env_name:str, region:str, project_name:str) -> None:
#     from threading import Event
#     received_event:Event = Event()

#     def on_message_received(topic:str, payload:dict, dup, qos, retain, **kwargs) -> None:
#         print(f"Received {payload} from {topic}")
#         received_event.set()

#     broker:Broker = Broker(env_name, region)
#     client:Client = broker.connect_for(project_name)
#     client.subscribe(callback=on_message_received, QoS=mqtt.QoS.AT_LEAST_ONCE)
#     client.publish(payload={'project name': project_name}, QoS=mqtt.QoS.AT_LEAST_ONCE)
#     print("Waiting for all messages to be received...")
#     received_event.wait()
#     client.disconnect()


# if __name__ == '__main__':
#     connect(
#         env_name = 'test',
#         region = 'us-east-1',
#         project_name = 'test',
#     )




# from account import Account
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
    def __init__(self, name:str='test') -> None:
        pass

    def create_client_using(self, certs_dir:str='test') -> Client:
        return Client()


class Region:
    def __init__(self, name:str='us-east-1') -> None:
        pass

    def create_project(self, name:str) -> Project:
        return Project(name)


class Account:
    def __init__(self, name:str='test') -> None:
        pass

    def use_region(self, name:str='us-east-1') -> Region:
        return Region(name)



# def provision_thing(self, name:str) -> Client:
#     fp:Project = self.create_project(name='fleet_provisioning')
#     claim:Client = fp.create_client_using(certs_dir='claim')
#     provisioning_connection:Connection = claim.connect()
#     thing_name:str = provisioning_connection.provision_thing(name)
#     client:Project = self.create_project(name=thing_name)
#     individual:Client = client.create_client_using(certs_dir=f'individual/{thing_name}')
#     return individual


test:Account = Account(name='test')
# burner:Account = Account(name='burner')

# virginia:Broker = test.use(region='us-east-1')
# tokyo:Broker = test.use(region='ap-northeast-1')

# client1:Client = virginia.provision_thing(name='client1')

# client1_connection:Connection = client1.connect()

# topic_aaa:Topic = client1_connection.use_topic(name='aaa')
# topic_bbb:Topic = client1_connection.use_topic(name='bbb')

# response:dict = topic_aaa.pub(message)
# response:dict = topic_aaa.sub(callback)
# response:dict = topic_aaa.unsub()

# response:dict = client1_connection.disconnect()