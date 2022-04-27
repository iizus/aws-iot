from client import read_config, connect

config:dict = read_config()
endpoint:str = config.get('endpoint')

folder:str = 'certs'
ca:str = f'{folder}/AmazonRootCA1.pem'

thing_name:str = 'sharing_cert1'
connect(endpoint, ca, thing_name, client_cert=f'{folder}/shared.pem')