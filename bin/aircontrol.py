#!/usr/bin/env python
import sys
import re

artist = ""
track = ""
album = ""

def extract(line):
    m = re.match('^(Title|Artist|Album Name): \"(.*?)\"\.$', line)
    if m:
        return m.group(1), m.group(2)
    m = re.match('has connected to this player', line)
    if m:
        return "Control", "Connected"
    m = re.match('has disconnected from this player', line)
    if m:
        return  "Control", "Disconnected"
    return None, None

def update(key, val):
    global artist, album, track
    if key == "Artist":
        artist = val
    elif key == "Album Name":
        album = val
    elif key == "Title":
         track = val

def render():
    print(f"{artist} - {album} - {track}")
    sys.stdout.flush()

# Main loop
try:
    while True:
        line = sys.stdin.readline()
        key, val = extract(line)
        if key and val:
            if key == "Control":
                print(f"{val}")
                sys.stdout.flush()
            else:
                update(key, val)
                render()

except KeyboardInterrupt:
    sys.stdout.flush()
    pass