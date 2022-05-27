from account import Account
from region import Region
from project import Project
from client import Client
# from connection import Connection
# from topic import Topic




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

virginia:Region = test.use_region(name='us-east-1')
tokyo:Region = test.use_region(name='ap-northeast-1')

test1:Project = virginia.create_project(name='test')
client1:Client = test1.create_client_using(certs_dir='')





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