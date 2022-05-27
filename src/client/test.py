from broker import Broker
from pubsub.pubsub import Client
from awscrt import mqtt


def connect(env_name:str, region:str, project_name:str) -> None:
    from threading import Event
    received_event:Event = Event()

    def on_message_received(topic:str, payload:dict, dup, qos, retain, **kwargs) -> None:
        print(f"Received {payload} from {topic}")
        received_event.set()

    broker:Broker = Broker(env_name, region)
    client:Client = broker.connect_for(project_name)
    client.subscribe(callback=on_message_received, QoS=mqtt.QoS.AT_LEAST_ONCE)
    client.publish(payload={'project name': project_name}, QoS=mqtt.QoS.AT_LEAST_ONCE)
    print("Waiting for all messages to be received...")
    received_event.wait()
    client.disconnect()


if __name__ == '__main__':
    connect(
        env_name = 'test',
        region = 'us-east-1',
        project_name = 'test',
    )