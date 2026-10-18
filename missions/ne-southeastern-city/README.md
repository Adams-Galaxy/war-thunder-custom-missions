# Nuclear Escalation — Southeastern City

These variants use Gaijin's official non-mirrored Southeastern City Nuclear
Escalation mission from the live game archive.

## Variants

| File | Strategic S-300 / SAMP/T sites | Russian-airfield HQ-11 | Other airfield AA |
|---|---|---|---|
| [`normal.blk`](normal.blk) | Enabled | Stock 30 km activation | Stock |
| [`sead-training-hq11-18km.blk`](sead-training-hq11-18km.blk) | Present and targetable, engagement channels disabled | 18 km sensor activation | Stock roster |
| [`no-long-range-sams.blk`](no-long-range-sams.blk) | All 16 groups removed | Stock 30 km activation | Stock |
| [`source.blk`](source.blk) | Enabled | Stock 30 km activation | Untouched extracted source |

The SEAD-training version uses the same zero-channel technique already tested
successfully on Archipelago. It leaves every strategic launcher and radar in
place for detection and attack, while setting both its missile and target
channel limits to zero. The five Team 1 airfields retain their normal Pantsir,
Tunguska, 2S38, and HQ-11 roster; only the HQ-11 sensor-activation radius is
changed from 30 km to 18 km.

The no-long-range-SAM version removes the complete dynamic object groups that
would instantiate S-300 or SAMP/T batteries in the 2018 era. Airfield and
point-defense groups are not removed.

### Direct URLs

Paste one of these into **Custom battles → Missions by URL**. If necessary,
remove `https://` first.

```text
https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-southeastern-city/normal.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-southeastern-city/sead-training-hq11-18km.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-southeastern-city/no-long-range-sams.blk
```

## Provenance

`source.blk` was decoded in canonical compact BLK form from the locally installed
`mis.vromfs.bin`. It preserves Gaijin's two internal import records for
provenance and is not itself a standalone URL mission. The three playable
variants expand the shared 64-player template and 2018 Nuclear Escalation ship
set, as required by the remote mission loader.

The mission points to `levels/air_south_eastern_city.bin` and contains eight
S-300-capable strategic groups, eight SAMP/T-capable strategic groups, and ten
2018 airfield-AA groups.
