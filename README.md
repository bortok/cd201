# cd201
Renovated harman/kardon cd201 cassette deck

## Raspberry Pi Setup

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

Build and install the metadata reader:

```Shell
git clone https://github.com/mikebrady/shairport-sync-metadata-reader.git
cd shairport-sync-metadata-reader
autoreconf -i -f
./configure
make
sudo make install
```

Test the metadata reader:

```Shell
cat /var/run/airplay/shairport-sync-metadata | shairport-sync-metadata-reader
```

Connect and play music. Airplay events:

* Connect

    ```
    The AirPlay client at "fe80::147e:28a7:18d6:2a0d" has connected to this player.
    ```

* Play

    ```
    Enter Active State.
    Play Session Begin.
    ```

* Pause

    ```
    Pause. (AirPlay 2 only.)
    ```

* Last song ends:

    ```
    Pause. (AirPlay 2 only.)
    ```
*  Disconnect

    ```
    Exit Active State.
    Play Session End.
    The AirPlay client at "fe80::147e:28a7:18d6:2a0d" has disconnected from this player. (AirPlay 2 only.)
    ```
