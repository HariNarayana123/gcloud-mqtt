import datetime
import ssl
import time
import jwt
import paho.mqtt.client as mqtt

connected = False
messagerecieved = False;
project_id = "halogen-byte-329812"
cloud_region = "us-central1"
registry_id = "my-python-registry"
device_id = "my-python-device"
private_key_file = "rsa_private.pem"
algorithm = "RS256"
ca_certs = "roots.pem"
mqtt_bridge_hostname = "mqtt.googleapis.com"
mqtt_bridge_port = 443

jwt_iat = datetime.datetime.utcnow()
jwt_exp_mins = 20


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print("on_connect", mqtt.connack_string(rc))
    global connected
    connected = True

def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = str(message.payload.decode("utf-8"))
    print(
        "Received message '{}' on topic '{}' with Qos {}".format(
            payload, message.topic, str(message.qos)
        )
    )

def create_jwt(project_id, private_key_file, algorithm):

    token = {
        # The time that the token was issued at
        "iat": datetime.datetime.utcnow(),
        # The time the token expires.
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=20),
        # The audience field should always be set to the GCP project id.
        "aud": project_id,
    }

    # Read the private key file.
    with open(private_key_file, "r") as f:
        private_key = f.read()

    print(
        "Creating JWT using {} from private key file {}".format(
            algorithm, private_key_file
        )
    )

    return jwt.encode(token, private_key, algorithm=algorithm)

client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
        project_id, cloud_region, registry_id, device_id
    )
topic = "/devices/{}/{}".format(device_id, "events")
#topic = "projects/halogen-byte-329812/topics/my-python-topic"
mqtt_command_topic = "/devices/{}/commands/#".format(device_id)
#mqtt_config_topic = "/devices/{}/config".format(device_id)

print("Client Id : {}\nTopic : {}\n".format(client_id, topic))

client = mqtt.Client(client_id=client_id)
client.on_message = on_message
client.username_pw_set(
        username="unused", password=create_jwt(project_id, private_key_file, algorithm)
    )
client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)
client.on_connect = on_connect


client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
client.loop_start()
print("loop start")

client.subscribe(mqtt_command_topic)

while connected != True:
    time.sleep(0.3)

print("Waiting for message")

while messagerecieved != True:
    time.sleep(0.3)

client.loop_stop()
