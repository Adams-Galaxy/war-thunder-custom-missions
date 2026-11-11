# Nuclear Escalation — Kamchatka / Volcano Valley (2018)

This family is generated from Gaijin's official 2018 **Kamchatka** Nuclear
Escalation mission, commonly called Volcano Valley. The source snapshot is
materialized from the current public datamine together with every required
internal template, so the published variants are standalone Custom Battles
missions rather than references to local game files.

## Variants

| File | Strategic SAMs | Other air defenses |
|---|---|---|
| [`normal.blk`](normal.blk) | Stock | Stock |
| [`sead-training-hq11-18km.blk`](sead-training-hq11-18km.blk) | Present and targetable, but unable to engage | HQ-11/SPYDER activation at 18 km |
| [`no-long-range-sams.blk`](no-long-range-sams.blk) | Present and targetable, but unable to engage | HQ-11/SPYDER 18 km, Pantsir 8 km, direct 2S6/Crotale 6 km |
| [`peaceful-exploration.blk`](peaceful-exploration.blk) | Present, zero engagement channels | Players are hidden from AI targeting and immortal |

The initial release preserves Kamchatka's official spawn topology. We will add
the custom quick-start aircraft, helicopter, and naval spawn package only
after testing those positions on the new terrain.

## Direct URLs

Paste one into **Custom Battles → Missions by URL**. If necessary, remove
`https://` before pasting.

```text
https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-kamchatka-2018/normal.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-kamchatka-2018/sead-training-hq11-18km.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-kamchatka-2018/no-long-range-sams.blk

https://raw.githubusercontent.com/Adams-Galaxy/war-thunder-custom-missions/main/missions/ne-kamchatka-2018/peaceful-exploration.blk
```

## Regeneration

The tracked `source.blk` is an immutable snapshot. To refresh it from the
locally cached current datamine, then regenerate the variants:

```sh
python3 tools/import_kamchatka_source.py
python3 tools/build_variants.py
```
