# Nuclear Escalation — Archipelago (2018)

## Variants

| File | Long-range S-300 / SAMP/T sites | Airfield AA, including HQ-11 | Status |
|---|---:|---:|---|
| [`source.blk`](source.blk) | Enabled | Enabled | Original |
| [`no-lrsam.blk`](no-lrsam.blk) | Removed; missile ships capped at 18 km | HQ-11/SPYDER 18 km, Pantsir 8 km, direct 2S6/Crotale sources 6 km | Easiest combat mode; quick-start spawns and 30-second respawn |
| [`no-lrsam-no-airfield-aa.blk`](no-lrsam-no-airfield-aa.blk) | Removed | Removed | Generated; needs in-game validation |
| [`silent-lrsam-experimental.blk`](silent-lrsam-experimental.blk) | Present, attempted zero-ammo override | Enabled | Tested: override ignored; sites still fire |
| [`sead-training-strategic-sams-silent.blk`](sead-training-strategic-sams-silent.blk) | Present, missile/target channels set to zero | Enabled | **Tested: strategic sites do not launch** |
| [`sead-training-hq11-18km.blk`](sead-training-hq11-18km.blk) | Present, unable to engage; missile ships capped at 18 km | HQ-11 sensor activation reduced to 18 km | Quick-start aircraft, helicopter, and naval spawns; 30-second respawn |
| [`sead-training-hq11-silent.blk`](sead-training-hq11-silent.blk) | Present, unable to engage | HQ-11 radar and initial missiles disabled | Experimental; needs in-game validation |
| [`experimental-quick-start-airspawns.blk`](experimental-quick-start-airspawns.blk) | Present, unable to engage; missile ships capped at 18 km | HQ-11 sensor activation reduced to 18 km | Experimental; 30-second respawn with aircraft, helicopter, and naval spawns |
| [`experimental-short-range-air-defenses.blk`](experimental-short-range-air-defenses.blk) | Present, unable to engage; missile ships capped at 18 km | HQ-11/SPYDER 18 km, Pantsir 8 km, direct 2S6/Crotale sources 6 km | Experimental; quick-start package enabled |
| [`peaceful-exploration.blk`](peaceful-exploration.blk) | Present, zero strategic engagement channels | Stock roster | Players are continuously hidden from AI targeting and immortal; quick-start package enabled |

`silent-lrsam-zero-channels-experimental.blk` remains available as a
compatibility alias for the previously published stable URL.

The maintained difficulty progression is normal, SEAD training with silent
strategic sites and otherwise unchanged shorter-range defenses, then the
no-strategic-SAM mode with reduced sensor envelopes. Peaceful exploration is
a separate non-combat option.

The shared quick-start package used by the two maintained non-normal variants
and the experiment places fields 1–3 at 1.5 km and fields
4–5 at 3.5 km, all 6 km behind their runways. The 7 km main spawn starts from
the halfway point between the main base and fields 4–5, then moves another
1.5 km toward friendly territory. It also adds helicopter-only spawns 300 m
above and 8 km forward of fields 1–3 toward the front line, plus two naval
spawns per team 3 km ahead of the carriers' initial positions and aligned with
their routes. Tanks are disabled in these quick-start variants.

The short-range-defense experiment applies its sensor envelopes to every
airfield, strongpoint, standalone AA-cover group, static fuel/ammo-factory
defense, and fuel/ammo convoy roster. Assembly areas create their later tank
factories from a protected built-in template, so SAM escorts in those future
tank/artillery columns retain their stock 12 km (2S6) or 15 km (Crotale)
sensor-activation radius. This is also a sensor wake-up limit rather than a
hard missile-flight cutoff.

The peaceful exploration variant retains the complete unit population so it
can be inspected. Every 0.25 seconds it marks all current player vehicles as
untargetable by AI and immortal, which also covers respawns and vehicle
changes. Strategic sites additionally retain their tested zero-channel
override. AI units may still fight other AI units if opposing forces meet.

### Direct URLs

Paste one of these into **Custom battles → Missions by URL**. If necessary,
remove `https://` first.

```text
https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/source.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/no-lrsam.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/no-lrsam-no-airfield-aa.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/silent-lrsam-experimental.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/sead-training-strategic-sams-silent.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/silent-lrsam-zero-channels-experimental.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/sead-training-hq11-18km.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/sead-training-hq11-silent.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/experimental-quick-start-airspawns.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/experimental-short-range-air-defenses.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/peaceful-exploration.blk
```

## Defense layers in the source mission

- 16 dynamic strategic SAM sites: eight S-300 and eight SAMP/T templates.
- 12 `airfield_aa_2018` instances. Team 1 airfields include HQ-11 units.
- 16 Western and 16 Soviet point-defense cover templates away from airfields.

Removing only the strategic site objects does not remove airfield or point
defenses.

## Silent-site experiments

The first experimental file kept the procedural S-300 and SAMP/T factories
and attempted to override their `sam_site__unitSettings` arrays. In-game
testing showed that multiplayer mission loading ignored the nested array and
the sites still fired.

The zero-channels experiment instead uses two ordinary scalar ECS components
that the server passes directly into `set_sam_site`: both missile and target
channel limits are set to zero. In-game testing confirmed that this preserves
the generated launcher and radar entities while preventing launches.

## HQ-11 variants

The HQ-11s at team 1 airfields are created by `airfield_aa_2018`. Its normal
sensor-activation radius is 30 km. The 18 km variant supplies a mission-local
generic airfield roster, which the server checks before the built-in team
roster, and changes only the HQ-11 radius to 18 km. This is a sensor wake-up
radius rather than a direct missile-flight limit, so the exact engagement
behavior needs an in-game test.

The silent HQ-11 variant uses the same higher-priority roster, starts HQ-11
radars disabled, gives them zero initial missiles, and sets the sensor wake-up
radius to zero. The other team-1 airfield defenses keep their original roster
and settings.

All maintained variants use English mission titles and descriptions. The
untouched `source.blk` retains the original Russian metadata for provenance.
