from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Account, Endpoint
from src.client.connection import Topic


test_env:Account = Account(name='test')
burner_env:Account = Account(name='burner')

test_virginia:Endpoint = test_env.get_endpoint_of(region='us-east-1')
test_tokyo:Endpoint = test_env.get_endpoint_of(region='ap-northeast-1')

test_virginia_443:Endpoint = test_virginia.set_port(443)
test_virginia_443_ca:Endpoint = test_virginia_443.set_ca(type='RSA2048')

test_project:Project = Project(name='test')

test_virginia.excute_callback_on(
    client = test_project.create_client(client_id='client1'),
    callback = publish_messages,
    topic = 'test/test1',
)
test_virginia.excute_callback_on(
    client = test_project.create_client(client_id='client2'),
    callback = publish_messages,
    topic = 'test/test2',
)