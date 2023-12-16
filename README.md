# cd201
Renovated harman/kardon cd201 cassette deck

## Raspberry Pi Setup

### MQTT Broker

```Shell
#sudo vi /usr/local/etc/mosquitto.conf
docker run -d --restart unless-stopped \
    --net=host \
    --name mqtt \
    eclipse-mosquitto
#    -v /usr/local/etc/mosquitto.conf:/mosquitto/config/mosquitto.conf \
```

### Audio HAT

Model: Inno-Maker Raspberry Pi HiFi DAC HAT PCM5122

```Shell
# Enable audio HAT in /boot/config.txt
sudo bash -c "cat >> /boot/config.txt" << EOF
dtoverlay=allo-boss-dac-pcm512x-audio
EOF
```

### Airplay

Enable metadata output in `/usr/local/etc/shairport-sync.conf`:

```Shell
sudo vi /usr/local/etc/shairport-sync.conf
metadata =
{
        enabled = "yes"; // set this to yes to get Shairport Sync to solicit metadata from the source and to pass it on via a pipe
        include_cover_art = "yes"; // set to "yes" to get Shairport Sync to solicit cover art from the source and pass it via the pipe. You must also set "enabled" to "yes".
        cover_art_cache_directory = "/tmp/shairport-sync/.cache/coverart"; // artwork will be  stored in this directory if the dbus or MPRIS interfaces are enabled or if the MQTT client is in use. Set it to "" to prevent caching, which may be useful on some systems
        pipe_name = "/airplay/shairport-sync-metadata";
        pipe_timeout = 5000; // wait for this number of milliseconds for a blocked pipe to unblock before giving up
        progress_interval = 0.0; // if non-zero, progress 'phbt' messages will be sent at the interval specified in seconds. A 'phb0' message will also be sent when the first audio frame of a play session is about to be played.
};
mqtt =
{
	enabled = "yes"; // set this to yes to enable the mqtt-metadata-service
	hostname = "localhost"; // Hostname of the MQTT Broker
	port = 1883; // Port on the MQTT Broker to connect to
//	username = "username"; //set this to a string to your username in order to enable username authentication
//	password = "password"; //set this to a string you your password in order to enable username & password authentication
	topic = "shairport"; //MQTT topic where this instance of shairport-sync should publish. If not set, the general.name value is used.
//	publish_raw = "no"; //whether to publish all available metadata under the codes given in the 'metadata' docs.
	publish_parsed = "yes"; //whether to publish a small (but useful) subset of metadata under human-understandable topics
	publish_cover = "no"; //whether to publish the cover over mqtt in binary form. This may lead to a bit of load on the broker
	enable_remote = "no"; //whether to remote control via MQTT. RC is available under `topic`/remote.
};
```

Explore the list of Alsa devices:

```Shell
docker run --rm --device /dev/snd mikebrady/sps-alsa-explore
```

In my setup the audio HAT is listed as `hw:2`:

```
> Device Full Name:    "hw:Headphones"
  Short Name:          "hw:0"
  This device seems suitable for use with Shairport Sync.
  Possible mixers:     "PCM",0                 Range: 106.38 dB
  The following rate and format would be chosen by Shairport Sync in "auto" mode:
     Rate              Format
     44100             S16_LE

> Device Full Name:    "hw:BossDAC"
  Short Name:          "hw:2"
  This device seems suitable for use with Shairport Sync.
  Possible mixers:     "Analogue",0            Range:   6.00 dB
                       "Digital",0             Range: 103.00 dB
                       "Analogue Playback Boost",0   Range:   0.80 dB
  The following rate and format would be chosen by Shairport Sync in "auto" mode:
     Rate              Format
     44100             S32_LE

```

Launch the Airplay server with name `Living Room`, audio device `hw:2` and mixer `Digital`:

```Shell
sudo mkdir -p /var/run/airplay
docker run -d --restart unless-stopped --net host --device /dev/snd --name airplay \
  -v /usr/local/etc/shairport-sync.conf:/etc/shairport-sync.conf  \
  -v /var/run/airplay:/airplay  \
  mikebrady/shairport-sync -a "Living Room" -- -d hw:2 -c Digital
```

### Airplay Metadata

1. Prepare the virtual environment (run once):

```Shell
git clone https://github.com/bortok/cd201.git
cd cd201
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
```

2. Use `aircontrol.py` to subscribe to the AirPlay events:

```Shell
source cd201/venv/bin/activate
./cd201/bin/aircontrol.py
```
