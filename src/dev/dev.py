from account import Account
from project import Project

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

test_virginia = test.get_endpoint_of(region='us-east-1')
test_tokyo = test.get_endpoint_of(region='ap-northeast-1')

test_virginia_8883 = test_virginia.set_port(number=8883)

# test1 = virginia.create_project(name='test')
# client1 = test1.create_client_using(certs_dir='')
# connection1 = client1.connect()


test1:Project = Project(name='test')
client1 = test1.create_client_using(certs_dir='')
connection1 = client1.connect_to(test_virginia)
# connection1 = client1.connect_to(test_virginia_8883)





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