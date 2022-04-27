from client import read_config, test

config:dict = read_config()
endpoint:str = config.get('endpoint')

folder:str = 'certs'
ca:str = f'{folder}/AmazonRootCA1.pem'

test(endpoint, ca, client_id='sharing_cert1', client_cert=f'{folder}/shared.pem')
test(endpoint, ca, client_id='sharing_cert2', client_cert=f'{folder}/shared.pem')