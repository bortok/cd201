#!/usr/bin/env python
import sys
import re

artist = ""
track = ""
album = ""

def match_and_parse(line):
    m = re.match('^(Title|Artist|Album Name): \"(.*?)\"\.$', line)
    if m:
        return m.group(1), m.group(2)
    m = re.match('.*has (connected|disconnected) (to|from) this player.*', line)
    if m:
        return "Connection", m.group(1)
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
        key, val = match_and_parse(line)
        if key and val:
            if key == "Connection":
                print(f"{val}")
                sys.stdout.flush()
            else:
                update(key, val)
                render()

except KeyboardInterrupt:
    sys.stdout.flush()
    pass