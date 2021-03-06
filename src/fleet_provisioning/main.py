from provisioning import provision
from ..client import read_config, connect

config:dict = read_config()
endpoint:str = config.get('endpoint')

folder:str = 'certs'
ca:str = f'{folder}/AmazonRootCA1.pem'

thing_name:str = provision(
    endpoint,
    ca,
    claim_cert = f'{folder}/claim.pem',
    template_name = config.get('template_name')
)
connect(endpoint, ca, thing_name, client_cert=f'{folder}/client.pem')