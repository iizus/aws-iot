from broker import read_config, Broker

config = read_config(file_path='config.json')
broker:Broker = Broker(config.endpoint, config.ca)

shared1 = broker.connect(
    cert = f'{config.client_cert}.crt',
    key = f'{config.client_cert}.key',
    client_id = 'shared_cert1',
)

shared1.publish(payload={'client_id': 'shared_cert1'})

shared1.disconnect()