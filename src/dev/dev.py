from account import Account, Endpoint, Port, Proxy
# import account
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

test_virginia:Endpoint = test.get_endpoint_of(region='us-east-1')
test_tokyo:Endpoint = test.get_endpoint_of(region='ap-northeast-1')

test_virginia_443:Port = test_virginia.set_port(number=443)
test_virginia_443_proxy:Proxy = test_virginia_443.set_proxy(host='0.0.0.0', port=443)

# test1 = virginia.create_project(name='test')
# client1 = test1.create_client_using(certs_dir='')
# connection1 = client1.connect()


test1:Project = Project(name='test')
client1 = test1.create_client_using(certs_dir='')
# connection2 = client1.connect_to(test_virginia)
connection1 = client1.connect_to(test_virginia_443)





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