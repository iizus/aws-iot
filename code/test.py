from client import read_config, test

config:dict = read_config()

endpoint:str = config.get('endpoint')
ca:str = config.get('ca')
client_cert:str = config.get('client_cert')

test(endpoint, ca, client_id='sharing_cert1', client_cert=client_cert)
test(endpoint, ca, client_id='sharing_cert2', client_cert=client_cert)