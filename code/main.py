def provision(endpoint:str, claim_cert:str, ca:str, template_name:str) -> str:
    from provisioning import Provisioning
    provisioning = Provisioning(endpoint, ca, template_name)

    from uuid import uuid4
    device_ID:str = str(uuid4())

    thing_name:str = provisioning.provision_thing_by(
        cert = f'{claim_cert}.crt',
        key = f'{claim_cert}.key',
        client_id = device_ID,
        template_parameters = {"DeviceID": device_ID},
    )
    return thing_name


def connect(endpoint:str, client_cert:str, ca:str, thing_name:str) -> None:
    from threading import Event
    received_event:Event = Event()

    def on_message_received(topic:str, payload:dict, dup, qos, retain, **kwargs) -> None:
        print(f"Received {payload} from {topic}")
        received_event.set()

    from client import Client, mqtt
    client:Client = Client(endpoint, ca)
    client.connect(
        cert = f'{client_cert}.crt',
        key = f'{client_cert}.key',
        client_id = thing_name,
    )
    client.subscribe(callback=on_message_received, QoS=mqtt.QoS.AT_LEAST_ONCE)
    client.publish(QoS=mqtt.QoS.AT_LEAST_ONCE)
    print("Waiting for all messages to be received...")
    received_event.wait()
    client.disconnect()


from client import read_config
config:dict = read_config(file_path='config.json')
endpoint:str = config.get('endpoint')
template_name:str = config.get('template_name')

folder:str = 'certs'
claim_cert:str = f'{folder}/claim.pem'
client_cert:str = f'{folder}/client.pem'
ca:str = f'{folder}/AmazonRootCA1.pem'

thing_name:str = provision(endpoint, claim_cert, ca, template_name)
connect(endpoint, client_cert, ca, thing_name)