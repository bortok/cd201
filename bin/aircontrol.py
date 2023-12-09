#!/usr/bin/env python
import sys
import re

artist = ""
track = ""
album = ""

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
    if key == "Artist":
        artist = val
    elif key == "Album Name":
        album = val
    elif key == "Title":
         track = val

def render_track_meta():
    print(f"{artist} - {album} - {track}")
    sys.stdout.flush()

# Main loop
try:
    while True:
        line = sys.stdin.readline()
        event, data = match_and_parse(line)
        if event and data:
            if event == "connection":
                send_connection_update(data[0], data[1])
            else:
                update_track_meta(data[0], data[1])
                render_track_meta()

except KeyboardInterrupt:
    sys.stdout.flush()
    pass