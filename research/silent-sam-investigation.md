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

## Next experiment

Test whether a multiplayer user mission may import or locally override an ECS
template that replaces only the launchers' `bulletsCount` with zero. This would
preserve the procedural layout and avoid manually placing 96 component units.

If server-side template overrides are rejected, the fallback is to generate
named units automatically from each site's transform—not to place them by hand.

## Data references

- War Thunder datamine, `templates/nuclear_escalation/sam_sites.blkx`
- War Thunder datamine, `templates/nuclear_escalation/airfields.blkx`
- War Thunder CDK action schema, `unitSetProperties.scheme.nut`
- War Thunder CDK action schema, `unitSetZeroAmmo.scheme.nut`
