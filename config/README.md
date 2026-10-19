# Dynamic mission configuration

`base.toml` is loaded first. Every file in `maps/` is recursively merged over
that base: nested tables retain unspecified defaults, while scalar values and
arrays replace the base value. Set `mission.enabled = false` in a map profile
to omit it from builds and the mission server.

Each map requires a unique URL-safe `mission.slug`. Its public route is always:

```text
/wt/missions/dynamic/<slug>.blk
```

## Defense settings

- `strategic_sams`: `stock`, `silent`, or `removed`.
- `hq11_mode`: `stock`, `range_limited`, or, on Archipelago, `silent`.
- `hq11_range_km`: sensor activation range used by `range_limited`.
- `missile_ship_range_km`: mission-level missile-ship engagement cap. Use
  `0.0` to leave the stock ship behavior unchanged.

## Rules

`rules` controls the player respawn delay and which vehicle families the room
allows. Enabling a custom spawn while its vehicle family is disabled is a
configuration error.

## Spawn settings

Archipelago currently supports all three custom spawn sections:

- Aircraft fields have an absolute altitude and rearward distance from their
  associated airfield.
- Helicopter fields use altitude above the field and distance toward the
  frontline. A positive `forward_from_field_m` moves toward the enemy; a
  negative value moves deeper into friendly territory.
- Naval spawns are derived from the carriers' initial transforms and route
  headings. `forward_from_carrier_m` controls how far ahead they appear.

Generated files under `build/dynamic/` are disposable and ignored by Git. The
configuration files are the version-controlled source of truth.
