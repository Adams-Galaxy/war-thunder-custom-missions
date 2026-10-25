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
table for all three proxy filenames. The installer registers that table and
enables War Thunder's `testLocalization` mode while preserving the user's
existing localization files.

## Loadout presentation

Each Rafale SCALP preset has an explicit `weaponConfig` containing exactly two
JSOW-style guided-weapon icons at the Rafale's heavy-station display tiers 10
and 2. The custom weapon and both station presets use the same icon type so the
in-battle action bar does not have to guess from the inherited Rafale catalog.

The installed physical loadout is unchanged:

- aircraft station 3: one SCALP-EG proxy;
- aircraft station 6: TALIOS targeting pod;
- aircraft station 10: one SCALP-EG proxy.

## Variants

The manifest records the two known-working optical/IR versions and the newer
coordinate-guided test. The INS version uses a seekerless SNS base, the normal
missile/ATGM release channel, a damped 150 m cruise, and an experimental
30 m descent / 120 m pop-up / 35-degree terminal dive. All share the same
physical approximation and 250 kg PBXN-110 gameplay fill. See `asset.toml` for
exact paths and tuning values.

The asset is local and single-player-only. It does not add a genuine SCALP 3D
model, TERPROM, terminal scene matching, tandem BROACH damage, or a multiplayer
vehicle modification.
