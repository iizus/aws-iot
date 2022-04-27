from client import read_config, Brocker

config = read_config(file_path='config.json')

broker:Brocker = Brocker(config.endpoint, config.ca)

shared1 = broker.connect(
    cert = f'{config.client_cert}.crt',
    key = f'{config.client_cert}.key',
    client_id = 'shared_cert1',
)
shared1.publish(payload={'client_id': 'shared_cert1'})
shared1.disconnect()