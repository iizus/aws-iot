from broker import read_config, Broker, Client

config = read_config(file_path='config.json')
broker:Broker = Broker(config.endpoint, config.ca)

shared1 = broker.connect(
    cert = f'{config.client_cert}.crt',
    key = f'{config.client_cert}.key',
    client_id = 'shared_cert1',
)
shared2 = broker.connect(
    cert = f'{config.client_cert}.crt',
    key = f'{config.client_cert}.key',
    client_id = 'shared_cert2',
)
shared3 = broker.connect(
    cert = f'{config.client_cert}.crt',
    key = f'{config.client_cert}.key',
    client_id = 'shared_cert3',
)

shared1.publish(payload={'client_id': shared1.client_id})
shared2.publish(payload={'client_id': shared2.client_id})
shared3.publish(payload={'client_id': shared3.client_id})

shared1.disconnect()
shared2.disconnect()
shared3.disconnect()