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
- Current visual/physics base: War Thunder's AGM-84K SLAM-ER asset

`bulletName` and `gunnerOpticsName` are overridden to `SCALP-EG`. War Thunder
therefore uses the correct short identity in the selected-weapon HUD instead of
the inherited AGM-84K identity. A complete translated long name would require a
custom localization table; this package deliberately avoids globally enabling
War Thunder's `testLocalization` mode because that would also activate every
other locally generated, potentially stale CSV file.

## Loadout presentation

Each Rafale SCALP preset has an explicit `weaponConfig` containing exactly two
large air-to-ground missile icons at the Rafale's heavy-station display tiers
10 and 2. This prevents the loadout preview from guessing based on the entire
inherited Rafale weapon catalog and displaying unrelated tanks or missiles.

The installed physical loadout is unchanged:

- aircraft station 3: one SCALP-EG proxy;
- aircraft station 6: TALIOS targeting pod;
- aircraft station 10: one SCALP-EG proxy.

## Variants

The manifest records the two known-working optical/IR versions and the newer
coordinate-guided low-altitude test. All share the same physical approximation
and 250 kg PBXN-110 gameplay fill. See `asset.toml` for exact paths and tuning
values.

The asset is local and single-player-only. It does not add a genuine SCALP 3D
model, TERPROM, terminal scene matching, tandem BROACH damage, or a multiplayer
vehicle modification.
