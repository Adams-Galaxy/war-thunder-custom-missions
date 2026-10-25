# SCALP-EG reusable gameplay asset

This directory is the catalog entry for the repository's SCALP-EG gameplay
proxy. The live BLK sources remain in the mirrored `content/pkg_local` tree so
they can be copied directly into War Thunder without a build step. `asset.toml`
is the stable, machine-readable description intended for a future mission and
loadout generator.

## Identity

- Official French service name: **SCALP-EG**
- Expanded French name: *Système de croisière conventionnel autonome à longue
  portée d’emploi général*
- British name for the same weapon family: **Storm Shadow**
- Current visual/aerodynamic base: War Thunder's AGM-84K SLAM-ER asset
- INS guidance base: War Thunder's seekerless Grom-1 SNS path

`bulletName` and `gunnerOpticsName` are overridden to `SCALP-EG`. The in-flight
selected-weapon HUD additionally derives a `/short` localization key from the
custom BLK filename, so the experiment ships an isolated English localization
table for every proxy filename. The installer registers that table and
enables War Thunder's `testLocalization` mode while preserving the user's
existing localization files.

## Loadout presentation

Each Rafale SCALP preset has an explicit `weaponConfig` containing exactly two
JSOW-style guided-weapon icons at the Rafale's heavy-station display tiers 10
and 2. The projectile retains the JSOW/JDAM icon identifier while the aircraft
configuration and station presets now use the same `glide_bomb_default` value
as the working JSOW loadouts. This is the closest available match for the
in-battle action bar, although the UI can still ignore custom-weapon icons.

The installed physical loadout is unchanged:

- aircraft station 3: one SCALP-EG proxy;
- aircraft station 6: TALIOS targeting pod;
- aircraft station 10: one SCALP-EG proxy.

## Variants

The manifest records the two known-working optical/IR versions, three earlier
coordinate-guided terminal tests, and twelve controlled terminal-turn profiles.
All INS versions use a seekerless SNS base,
the normal missile/ATGM release channel, and the proven medium damping. One is
the known-good ultra-late reference; the other two use five altitude keyframes
to hold a 35–40 m terminal approach until five seconds from impact before
distinct 600 m and deliberately exaggerated 1,000 m pop-ups. All three use an
equilateral flat-water test range with two stationary 12 km targets. The twelve-profile
matrix holds the commanded apex at 600 m while independently varying descent
lead, climb-angle cap, and climb gain. Four profiles share the softened 0.0125
gain and 45-degree cap while tightening descent timing from 2.5 to 1.5 seconds.
Three additional profiles continue to 1.25, 1.0, and 0.75 seconds with a small
further reduction in target omega and vertical-rate gain. A ground-range mission
reuses the 1.0-second profile from NATO Air Spawn 1 at 1.5 km.
Three geometry-driven alternatives remove the terminal time-to-altitude
schedule entirely: moderate and steep native-loft profiles, plus an explicitly
experimental hybrid that combines constant 35 m altitude hold with the steep
native loft controller. Each geometry profile has water and ground missions.
These terminal-profile tests spawn at 100 m facing the midpoint between the
ships because the global descent-angle limiter needed for a safe high release
would also constrain the terminal dive. Their inherited Grom rocket flame and
smoke are replaced by the AGM-84K turbojet-style effects. All variants share
the same physical approximation and 250 kg PBXN-110 gameplay fill. See
`asset.toml` for exact paths and tuning values.

Each INS test is a complete standalone BLK that directly includes the stock
Grom-1 definition. War Thunder fatally crashed when the responsive variants
were implemented by including the first custom INS BLK, so custom-on-custom
weapon inheritance is deliberately avoided even though it duplicates tuning.

The asset is local and single-player-only. It does not add a genuine SCALP 3D
model, TERPROM, terminal scene matching, tandem BROACH damage, or a multiplayer
vehicle modification.
