from sys import path
from os.path import dirname
current_dir:str = path[0]
parent_dir:str = dirname(current_dir)
path.append(parent_dir)



from src.client.account import Account, Endpoint, Project
from src.client.connection import Topic


def publish_10_messages(topic:Topic) -> None:
    for i in range(3):
        topic.publish(message={'client': topic.client_id, 'times': i})


test_env:Account = Account(name='test')
burner_env:Account = Account(name='burner')

test_virginia:Endpoint = test_env.get_endpoint_of(region='us-east-1')
test_tokyo:Endpoint = test_env.get_endpoint_of(region='ap-northeast-1')

test_virginia_443:Endpoint = test_virginia.set_port(443)
test_virginia_443_ca:Endpoint = test_virginia_443.set_ca(type='RSA2048')
fp:Endpoint = test_virginia.set_FP(template_name='ec2')

test_project:Project = Project(name='test')
test_virginia.setup_connection(
    client = test_project.create_client(),
    callback = publish_10_messages,
    topic = 'test/test',
)