# Sound Effects

This directory contains default sound effects for Bongo Cat. These are simple, programmatically-generated sounds that you can use or replace with your own.

## Included Sound Files

The following sound files are included by default:

- **slap.wav** - Regular slap sound (plays on most inputs)
- **slap_alt.wav** - Alternate slap sound (randomly selected)
- **combo.wav** - Combo milestone sound (plays at combo thresholds)
- **combo_high.wav** - High combo sound (plays at 30+ combo)
- **achievement.wav** - Achievement unlocked sound

## Supported Formats

- **WAV** (recommended) - Best compatibility
- **OGG** - Good compression, widely supported
- **MP3** - Supported but may require additional codecs

## Where to Get Sounds

You can:
1. Create your own sounds
2. Use royalty-free sound libraries (freesound.org, zapsplat.com)
3. Record your own audio
4. Download community sound packs (check discussions/releases)

## Enabling Sounds

1. Place sound files in this directory
2. Launch Bongo Cat
3. Right-click → Settings → Sound Effects → Enable
4. Adjust volume in Settings → Sound Volume

## Replacing Default Sounds

The included sounds are simple beeps generated programmatically. To use custom sounds:

1. Replace any of the WAV files with your own sounds
2. Keep the same filenames
3. Restart Bongo Cat to hear the new sounds

## Notes

- Sounds are completely optional
- Missing sound files will be silently skipped
- The app gracefully handles missing pygame/mixer
- Default sounds are programmatically generated (no copyright issues)
