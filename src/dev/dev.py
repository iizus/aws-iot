from account import Account, Endpoint, Port, Proxy
from project import Project

# def provision_thing(self, name:str) -> Client:
#     fp:Project = self.create_project(name='fleet_provisioning')
#     claim:Client = fp.create_client_using(certs_dir='claim')
#     provisioning_connection:Connection = claim.connect()
#     thing_name:str = provisioning_connection.provision_thing(name)
#     client:Project = self.create_project(name=thing_name)
#     individual:Client = client.create_client_using(certs_dir=f'individual/{thing_name}')
#     return individual



from time import sleep
from awscrt.mqtt import QoS

def subscribe_callback(topic:str, payload:str, dup, qos, retain, **kwargs) -> None:
    print(topic)
    print(payload)


test:Account = Account(name='test')
burner:Account = Account(name='burner')

test_virginia:Endpoint = test.get_endpoint_of(region='us-east-1')
test_tokyo:Endpoint = test.get_endpoint_of(region='ap-northeast-1')

test_virginia_443:Port = test_virginia.set_port(number=443)
# test_virginia_443_proxy:Proxy = test_virginia_443.set_proxy(host='0.0.0.0', port=443)

# test1 = virginia.create_project(name='test')
# client1 = test1.create_client_using(certs_dir='')
# connection1 = client1.connect()


test1:Project = Project(name='test')

test1_client1 = test1.create_client(client_id='client1')
test1_client2 = test1.create_client(client_id='client2')

test1_client1_connection = test1_client1.connect_to(test_virginia_443, clean_session=True)
test1_client2_connection = test1_client2.connect_to(test_virginia_443, clean_session=True)

client1_topic1 = test1_client1_connection.use_topic('bbb', QoS=QoS.AT_MOST_ONCE)
# client1_topic2 = test1_client1_connection.use_topic(QoS=QoS.AT_MOST_ONCE)

# client1_topic2.subscribe(subscribe_callback)


# client1_topic1.publish(message={'client ID': client1_topic1.client_id})
# client1_topic2.publish(message={'client ID': client1_topic2.client_id})

client2_topic1 = test1_client2_connection.use_topic('bbb', QoS=QoS.AT_MOST_ONCE)
client1_topic1.subscribe(callback=subscribe_callback)
test1_client1_connection.disconnect()
sleep(1)
client2_topic1.publish(message={'client ID': client2_topic1.client_id})
sleep(1)
test1_client1_connection = test1_client1.connect_to(test_virginia_443, clean_session=False)
client1_topic1 = test1_client1_connection.use_topic('bbb', QoS=QoS.AT_MOST_ONCE)
client1_topic1.subscribe(callback=subscribe_callback)
# test1_client1_connection.resubscribe_all_topics()
# client2_topic1.publish(message={'client ID': client2_topic1.client_id})
# client1_topic1.unsubscribe()
# client1_topic2.unsubscribe()

sleep(3)
# test1_client1_connection.disconnect()
test1_client2_connection.disconnect()

# sleep(3)
# # test1_client_connection = test1_client.connect_to(test_virginia_443, clean_session=True)
# client1_topic1.publish(message={'client ID': client1_topic1.client_id})
# client1_topic2.publish(message={'client ID': client1_topic2.client_id})
# sleep(3)
# test1_client_connection.resubscribe_all_topics()




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