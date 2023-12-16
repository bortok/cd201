#!/usr/bin/env python
import sys
import os
import re
import requests
import random

from paho.mqtt import client as mqtt_client

broker = "localhost"
port = 1883
topic_prefix = "shairport"
client_id = f"aircontrol-{random.randint(0, 1000)}"
# username = 'emqx'
# password = 'public'

meta_topics = ["artist", "album", "title"]
session_topics = ["active_start", "active_end"]

POWER_CRTL_ON_URL  = ""
POWER_CRTL_OFF_URL = ""

artist = ""
track  = ""
album  = ""


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
        if topic in meta_topics:
            update_track_meta(topic, msg.payload.decode())
            render_track_meta()
        elif topic in session_topics:
            send_connection_update(topic, msg.payload.decode())


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
    if event == "active_start":
        print(f"airplay is active")
        send_power_ctrl_request("on")
    elif event == "active_end":
        print(f"airplay is inactive")
        send_power_ctrl_request("off")
    sys.stdout.flush()

def send_power_ctrl_request(state):
    if POWER_CRTL_ON_URL == "" or POWER_CRTL_OFF_URL == "":
        print("POWER_CRTL_ON/OFF_URL is not set")
        return

    if state == "on":
        url = POWER_CRTL_ON_URL
    elif state == "off":
        url = POWER_CRTL_OFF_URL
    else:
        print("invalid state")
        return

    try:
        r = requests.get(url)
        print(f"power control request sent: {r.status_code}")
    except Exception as e:
        print(f"power control request failed: {e}")

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
    global POWER_CRTL_ON_URL, POWER_CRTL_OFF_URL
    POWER_CRTL_ON_URL  = os.getenv('POWER_CRTL_ON_URL',  '')
    POWER_CRTL_OFF_URL = os.getenv('POWER_CRTL_OFF_URL', '')

    topics = meta_topics + session_topics
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