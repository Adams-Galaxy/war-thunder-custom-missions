# Silent strategic SAM investigation

Goal: keep each S-300/SAMP/T site visible, radar-emitting, targetable, and
destructible for SEAD practice while preventing missile launches.

## Confirmed behavior

- Removing the 16 `sam_site_s300` / `sam_site_sampt` object groups removes the
  strategic SAM sites and their launches.
- `active:b=no` on the dynamic object-group wrapper does not stop the server
  from constructing the site.
- Repeated `unitSetProperties { cannotShoot:b=yes }` against the wrapper does
  not stop launches.
- Setting `sam_site__max_attackers_per_target:i=0` does not stop launches.

## Why the trigger approach failed

The object group is a server-side factory/controller, not one of the generated
units accepted by `unitSetProperties`. The S-300 template creates four
`ussr_ai_sam_launcher_5p85se` launchers, one `ussr_ai_sam_radar_5n63s`
tracking radar, and one `ussr_ai_sam_radar_5n64s` search radar. The SAMP/T
template creates four `it_samp_t_launcher` launchers and two `it_samp_t_fcs`
units.

## Zero-ammo experiment (failed)

`silent-lrsam-experimental.blk` overrides the existing
`sam_site__unitSettings:array` inside each mission object. The copied settings
retain the procedural launcher/radar composition but give launchers a
`bulletsCount` of zero and a rearm time of 1,000,000,000 seconds.

The game-side `sam_sites.das` implementation confirms that these values are
read from the settings array and passed to each generated launcher as
`setting__bulletsCount` and `unit_params__rearmTimeOnField`.

In-game testing established that multiplayer URL mission loading ignored this
nested array override: the generated sites retained their standard ammunition
and fired normally.

## Zero-channel experiment

`silent-lrsam-zero-channels-experimental.blk` sets
`sam_site__missile_channels_max` and `sam_site__target_channels_max` to zero on
every strategic site. These scalar components are passed directly to the
server-side `set_sam_site` call and avoid attempting to replace the protected
unit-settings array. The meaning of a zero channel limit needs an in-game test.

If a zero channel limit is treated as unlimited or ignored, the fallback is to
generate named units automatically from each site's transform—not to place
them by hand. The factory-created child units cannot be targeted by mission
actions because the factory gives them entity IDs but no mission-editor names.

## Data references

- War Thunder datamine, `templates/nuclear_escalation/sam_sites.blkx`
- War Thunder datamine, `templates/nuclear_escalation/airfields.blkx`
- War Thunder CDK action schema, `unitSetProperties.scheme.nut`
- War Thunder CDK action schema, `unitSetZeroAmmo.scheme.nut`
