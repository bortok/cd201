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

Explore the list of Alsa devices:

```Shell
docker run --rm --device /dev/snd mikebrady/sps-alsa-explore
```

My output with the audio HAT listed as `hw:2`:

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

Launch the Airplay server with name "Living Room", audio device `hw:2` and mixer `Digital`:

```Shell
sudo mkdir -p /var/run/airplay
docker run -d --restart unless-stopped --net host --device /dev/snd --name airplay \
  -v /usr/local/etc/shairport-sync.conf:/etc/shairport-sync.conf  \
  -v /var/run/airplay:/airplay  \
  mikebrady/shairport-sync -a "Living Room" -- -d hw:2 -c Digital
```