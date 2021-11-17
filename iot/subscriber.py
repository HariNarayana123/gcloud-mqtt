import os
from google.cloud import pubsub_v1

def callback(message):
    print(f'message {message}')
    print(f'data {message.data}')
    message.ack()

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "halogen-byte-key.json"
subscriber = pubsub_v1.SubscriberClient()
streaming_pull_future = subscriber.subscribe("projects/halogen-byte-329812/subscriptions/my-python-subscription", callback=callback)

with subscriber:
    try:
        streaming_pull_future.result()
    except TimeoutError:
        streaming_pull_future.cancel()
        streaming_pull_future.result()



