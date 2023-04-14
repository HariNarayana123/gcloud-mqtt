import argparse
import datetime
import ssl
import time
import jwt
import paho.mqtt.client as mqtt
import json

connected = False
messagerecieved = False;
private_key_file = "rsa_private.pem"
algorithm = "RS256"
ca_certs = "roots.pem"
mqtt_bridge_hostname = "mqtt.googleapis.com"
mqtt_bridge_port = 443

jwt_iat = datetime.datetime.utcnow()
jwt_exp_mins = 20

parser = argparse.ArgumentParser(description=("Arg Parse"))
parser.add_argument("--project_id", required=True)
parser.add_argument("--cloud_region", required=True)
parser.add_argument("--registry_id", required=True)
parser.add_argument("--device_id", required=True)
args = parser.parse_args()

project_id = args.project_id
cloud_region = args.cloud_region
registry_id = args.registry_id
device_id = args.device_id



def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print("on_connect", mqtt.connack_string(rc))
    global connected
    connected = True

def on_message(unused_client, unused_userdata, message):
    """Callback when the device receives a message on a subscription."""
    payload = message.payload.decode("utf-8")
    
    data  =json.loads(payloads)
    print(data["soil_moisture"])
    print(data["rainfall"])
 

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

#topic = "projects/halogen-byte-329812/topics/my-python-topic"
#mqtt_command_topic = "/devices/{}/commands/#".format(device_id)
#mqtt_config_topic = "/devices/{}/config".format(device_id)

print("Client Id : {}\nTopic : {}\n".format(client_id, topic))

client = mqtt.Client(client_id=client_id)

client.username_pw_set(
        username="unused", password=create_jwt(project_id, private_key_file, algorithm)
    )
client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

client.on_message = on_message
client.on_connect = on_connect


client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
client.loop_start()
print("loop start")


topic = "/devices/{}/{}".format("device-2", "events")
client.subscribe(topic)

while connected != True:
    time.sleep(0.3)

print("Waiting for message")

while messagerecieved != True:
    time.sleep(0.3)

client.loop_stop()
