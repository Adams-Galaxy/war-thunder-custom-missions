# Nuclear Escalation — Archipelago (2018)

## Variants

| File | Long-range S-300 / SAMP/T sites | Airfield AA, including HQ-11 | Status |
|---|---:|---:|---|
| [`source.blk`](source.blk) | Enabled | Enabled | Original |
| [`no-lrsam.blk`](no-lrsam.blk) | Removed | Enabled | Tested: long-range sites absent |
| [`no-lrsam-no-airfield-aa.blk`](no-lrsam-no-airfield-aa.blk) | Removed | Removed | Generated; needs in-game validation |
| [`silent-lrsam-experimental.blk`](silent-lrsam-experimental.blk) | Present, attempted zero-ammo override | Enabled | Tested: override ignored; sites still fire |
| [`silent-lrsam-zero-channels-experimental.blk`](silent-lrsam-zero-channels-experimental.blk) | Present, missile/target channels set to zero | Enabled | Experimental; needs in-game validation |

### Direct URLs

Paste one of these into **Custom battles → Missions by URL**. If necessary,
remove `https://` first.

```text
https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/source.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/no-lrsam.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/no-lrsam-no-airfield-aa.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/silent-lrsam-experimental.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-archipelago-2018/silent-lrsam-zero-channels-experimental.blk
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
channel limits are set to zero. This should preserve the generated launcher
and radar entities; its exact zero-limit behavior must be established in game.
