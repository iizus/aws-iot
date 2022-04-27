from client import read_config, test

config = read_config()

test(config.endpoint, config.ca, client_id='sharing_cert1', client_cert=config.client_cert)
test(config.endpoint, config.ca, client_id='sharing_cert2', client_cert=config.client_cert)