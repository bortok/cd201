#!/usr/bin/env python
import sys
import re
import random

from paho.mqtt import client as mqtt_client

broker = "localhost"
port = 1883
topic_prefix = "shairport"
client_id = f"aircontrol-{random.randint(0, 1000)}"
# username = 'emqx'
# password = 'public'

artist = ""
track = ""
album = ""


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(topic, client: mqtt_client):
    def on_message(client, userdata, msg):
        #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        parse_mqtt_msg(msg)

    client.subscribe(f"{topic_prefix}/{topic}")
    client.on_message = on_message


def parse_mqtt_msg(msg):
    topic = msg.topic.split("/")[-1]
    if len(topic) > 0:
        #print(f"Received {msg.payload.decode()} from {topic} topic")
        if topic in ["artist", "album", "title"]:
            update_track_meta(topic, msg.payload.decode())
            render_track_meta()


# no longer used
def match_and_parse(line):
    m = re.match('^(Title|Artist|Album Name): \"(.*?)\"\.$', line)
    if m:
        return "metadata", [m.group(1), m.group(2)]
    m = re.match('^The AirPlay client at \"(.*?)\" has (connected|disconnected) (to|from) this player.*', line)
    if m:
        return "connection", [m.group(2), m.group(1)]
    return None, None

def send_connection_update(event, client):
    if event == "connected":
        print(f"airplay_connect with {client}")
    elif event == "disconnected":
        print(f"airplay_disconnect with {client}")
    sys.stdout.flush()

def update_track_meta(key, val):
    global artist, album, track
    if key == "artist":
        artist = val
    elif key == "album":
        album = val
    elif key == "title":
         track = val

def render_track_meta():
    print(f"{artist} - {album} - {track}")
    sys.stdout.flush()

def main():
    """Main loop."""
    topics = ["artist", "album", "title"]
    client = connect_mqtt()
    for topic in topics:
        subscribe(topic, client)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        sys.stdout.flush()
        pass

    return 0

if __name__ == '__main__':
    sys.exit(main())