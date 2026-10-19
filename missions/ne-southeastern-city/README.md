# Nuclear Escalation — Southeastern City

These variants use Gaijin's official non-mirrored Southeastern City Nuclear
Escalation mission from the live game archive.

## Variants

| File | Strategic S-300 / SAMP/T sites | Russian-airfield HQ-11 | Gameplay package |
|---|---|---|---|
| [`normal.blk`](normal.blk) | Enabled | Stock 30 km activation | Stock |
| [`sead-training-hq11-18km.blk`](sead-training-hq11-18km.blk) | Present and targetable, engagement channels disabled | 18 km sensor activation | Quick-start spawns, 18 km missile ships, 30-second respawn |
| [`no-long-range-sams.blk`](no-long-range-sams.blk) | All 16 groups removed | Stock 30 km activation | Quick-start spawns, 18 km missile ships, 30-second respawn |
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

Both non-normal variants enable aircraft, helicopters, and ships while keeping
tanks disabled. Aircraft spawns for fields 1–2 are 1.5 km high and 6 km behind
their runways; fields 3–4 are 3.5 km high and 6 km behind. The 7 km main spawn
starts halfway toward fields 3–4 and then moves 1.5 km back toward friendly
territory. Helicopter-only spawns are 300 m above and 8 km forward of fields
1–2 toward the front line. Two naval spawns per team sit 3 km ahead of the
carriers' initial positions and follow their starting headings.

All three playable variants quote the eight fuel/ammo template keys containing
`+`. The game's local tooling accepts those keys unquoted, but its remote custom
mission parser rejects them and reports only `Mission download failed`.

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
set, as required by the remote mission loader. They also discard inactive
1970/1980 `rankRange` branches, leaving the same 2018-only structure used by
the working Archipelago custom mission.

The mission points to `levels/air_south_eastern_city.bin` and contains eight
S-300-capable strategic groups, eight SAMP/T-capable strategic groups, and ten
2018 airfield-AA groups.
