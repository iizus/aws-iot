from broker import read_config, Broker, mqtt

config = read_config(file_path='configs/config.json')
broker:Broker = Broker(config.endpoint, config.ca)

shared1 = broker.connect(
    cert = f'{config.client_cert}.crt',
    key = f'{config.client_cert}.key',
    client_id = 'sharing_cert1',
)
shared2 = broker.connect(
    cert = f'{config.client_cert}.crt',
    key = f'{config.client_cert}.key',
    client_id = 'sharing_cert2',
)
# shared3 = broker.connect(
#     cert = f'{config.client_cert}.crt',
#     key = f'{config.client_cert}.key',
#     client_id = 'sharing_cert3',
# )

shared1.publish(topic=f"test/{shared1.client_id}", payload={'client_id': shared1.client_id}, QoS=mqtt.QoS.AT_LEAST_ONCE)
shared2.publish(topic=f"test/{shared2.client_id}", payload={'client_id': shared2.client_id}, QoS=mqtt.QoS.AT_LEAST_ONCE)
# shared2.publish(topic=shared3.client_id, payload={'client_id': shared3.client_id}, QoS=mqtt.QoS.AT_LEAST_ONCE)

shared1.disconnect()
shared2.disconnect()
# shared3.disconnect()