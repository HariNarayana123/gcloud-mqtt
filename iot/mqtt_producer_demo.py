import argparse
import datetime
import ssl
import time
import jwt
import paho.mqtt.client as mqtt

connected = False
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

def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print("on_publish")

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

parser = argparse.ArgumentParser(description=("Arg Parse"))
parser.add_argument("--project_id", required=True)
parser.add_argument("--cloud_region", required=True)
parser.add_argument("--registry_id", required=True)
parser.add_argument("--device_id", required=True)
parser.add_argument("--temperature", required=True)
args = parser.parse_args()

project_id = args.project_id
cloud_region = args.cloud_region
registry_id = args.registry_id
device_id = args.device_id
payload = args.temperature

client_id = "projects/{}/locations/{}/registries/{}/devices/{}".format(
        project_id, cloud_region, registry_id, device_id
    )
topic = "/devices/{}/{}".format(device_id, "events")

print("Client Id : {}\nTopic : {}\npayload : {}".format(client_id, topic, payload))

client = mqtt.Client(client_id=client_id)
client.username_pw_set(
        username="unused", password=create_jwt(project_id, private_key_file, algorithm)
    )
client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(mqtt_bridge_hostname, mqtt_bridge_port)
client.loop_start()
print("loop start")


while connected != True:
    time.sleep(0.3)

client.publish(topic, payload)
client.loop_stop()
