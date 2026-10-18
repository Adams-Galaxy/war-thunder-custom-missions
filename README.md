# War Thunder custom missions

Version-controlled custom missions and variants for War Thunder.

## Missions

- [Nuclear Escalation — Archipelago (2018)](missions/ne-archipelago-2018/README.md)
- [Nuclear Escalation — Southeastern City](missions/ne-southeastern-city/README.md)

The `.blk` links in each mission folder are intended for War Thunder's
**Missions by URL** menu. If the game rejects a URL, remove the `https://`
prefix before pasting it.

## Development

Regenerate maintained variants with:

```sh
python3 tools/build_variants.py
```

`source.blk` is kept unchanged. Generated variants carry a visible title tag
so the loaded version can be verified in game.
