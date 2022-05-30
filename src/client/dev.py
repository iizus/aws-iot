from account import Account, Endpoint
from client.client import Project

# def provision_thing(self, name:str) -> Client:
#     fp:Project = self.create_project(name='fleet_provisioning')
#     claim:Client = fp.create_client_using(certs_dir='claim')
#     provisioning_connection:Connection = claim.connect()
#     thing_name:str = provisioning_connection.provision_thing(name)
#     client:Project = self.create_project(name=thing_name)
#     individual:Client = client.create_client_using(certs_dir=f'individual/{thing_name}')
#     return individual



from time import sleep
# from awscrt.mqtt import QoS




test_env:Account = Account(name='test')
burner_env:Account = Account(name='burner')

test_virginia:Endpoint = test_env.get_endpoint_of(region='us-east-1')
test_tokyo:Endpoint = test_env.get_endpoint_of(region='ap-northeast-1')

# test_virginia_443:Port = test_virginia.set_port(number=443)

test:Project = Project(name='test')

test_subscriber = test.create_client(client_id='client1')
test_publisher = test.create_client(client_id='client2')

test_subscriber_connection = test_subscriber.connect_to(test_virginia)
test_publisher_connection = test_publisher.connect_to(test_virginia)

topic:str = 'test/test'
subscriber_topic_test = test_subscriber_connection.use_topic(topic)
publisher_topic_test = test_publisher_connection.use_topic(topic)

subscriber_topic_test.subscribe()
publisher_topic_test.publish()
sleep(2)
subscriber_topic_test.unsubscribe()
sleep(2)
test_subscriber_connection.disconnect()
test_publisher_connection.disconnect()



# if __name__ == '__main__':
#     from doctest import testmod
#     testmod()