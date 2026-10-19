# Nuclear Escalation — Southeastern City

These variants use Gaijin's official non-mirrored Southeastern City Nuclear
Escalation mission from the live game archive.

## Variants

| File | Strategic S-300 / SAMP/T sites | Russian-airfield HQ-11 | Gameplay package |
|---|---|---|---|
| [`normal.blk`](normal.blk) | Enabled | Stock 30 km activation | Stock |
| [`sead-training-hq11-18km.blk`](sead-training-hq11-18km.blk) | Present and targetable, engagement channels disabled | HQ-11 and SPYDER at 18 km | Quick-start spawns, 18 km missile ships, 30-second respawn |
| [`no-long-range-sams.blk`](no-long-range-sams.blk) | Present and targetable, engagement channels disabled | HQ-11/SPYDER 18 km, Pantsir 8 km, direct 2S6/Crotale sources 6 km | Easiest combat mode; quick-start spawns and 30-second respawn |
| [`peaceful-exploration.blk`](peaceful-exploration.blk) | Present, zero engagement channels | Stock roster | Players are continuously hidden from AI targeting and immortal; quick-start package enabled |
| [`source.blk`](source.blk) | Enabled | Stock 30 km activation | Untouched extracted source |

The SEAD-training version uses the same zero-channel technique already tested
successfully on Archipelago. It leaves every strategic launcher and radar in
place for detection and attack, while setting both its missile and target
channel limits to zero. The five Team 1 airfields retain their normal Pantsir,
Tunguska, 2S38, and HQ-11 roster; only the HQ-11 sensor-activation radius is
changed from 30 km to 18 km.

The easy version keeps every S-300 and SAMP/T battery physically present and
targetable but gives the strategic sites zero engagement channels. It also
reduces the directly configurable shorter-range sensor envelopes: 2S6 and
Crotale to 6 km, Pantsir to 8 km, and both HQ-11 and SPYDER to 18 km.

The maintained difficulty progression is normal, SEAD training with silent
strategic sites plus 18 km HQ-11/SPYDER and missile ships, then easy mode with
the same physical strategic sites disabled and reduced shorter-range sensor
envelopes. Peaceful exploration is a separate non-combat option. The legacy
`no-long-range-sams.blk` filename is retained so its published URL does not
break; its strategic batteries are no longer removed.

All three enhanced variants enable aircraft, helicopters, and ships while keeping
tanks disabled. Aircraft spawns for fields 1–2 are 1.5 km high and 6 km behind
their runways; fields 3–4 are 3.5 km high and 6 km behind. The 7 km main spawn
starts halfway toward fields 3–4 and then moves 1.5 km back toward friendly
territory. Helicopter-only spawns are 300 m above and 8 km forward of fields
1–2 toward the front line. Two naval spawns per team sit 3 km ahead of the
carriers' initial positions and follow their starting headings.

All four playable variants quote the eight fuel/ammo template keys containing
`+`. The game's local tooling accepts those keys unquoted, but its remote custom
mission parser rejects them and reports only `Mission download failed`.

The reduced-range overrides cover airfields, strongpoints, standalone AA,
static fuel/ammo-factory defenses, and fuel/ammo convoys. SAM escorts created
later by assembly-built tank factories retain their protected stock templates.
The peaceful mode is not affected by that exception because it protects the
player rather than modifying each enemy unit: every 0.25 seconds it marks all
current player vehicles untargetable by AI and immortal.

### Direct URLs

Paste one of these into **Custom battles → Missions by URL**. If necessary,
remove `https://` first.

```text
https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-southeastern-city/normal.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-southeastern-city/sead-training-hq11-18km.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-southeastern-city/no-long-range-sams.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-southeastern-city/peaceful-exploration.blk
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
