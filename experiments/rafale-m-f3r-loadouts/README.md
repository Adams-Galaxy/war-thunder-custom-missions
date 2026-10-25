# Rafale M F3-R local weapon experiments

This is an intentionally local, single-player-only experiment built on the
peaceful South-Eastern City mission. It does not alter the stock Rafale or any
hosted multiplayer mission.

The package adds one custom unit based on `rafale_m_f3r` and sixteen missions:

- `Southeastern City · Rafale M · 8× SPICE 250`
- `Southeastern City · Rafale M · 6× Brimstone DM`
- `Southeastern City · Rafale M · 2× AGM-154A1 JSOW`
- `Southeastern City · Rafale M · 5× AGM-154A1 JSOW`
- `Southeastern City · Rafale M · 9× AGM-154A1 JSOW`
- `Southeastern City · Rafale M · 6× AGM-65D Maverick`
- `Southeastern City · Rafale M · 6× AGM-65G Maverick`
- `Southeastern City · Rafale M · 12× AGM-65G Maverick`
- `Southeastern City · Rafale M · 3× AGM-84H SLAM-ER`
- `Southeastern City · Rafale M · 5× AGM-84K SLAM-ER`
- `Southeastern City · Rafale M · 4× Kh-38MT`
- `Southeastern City · Rafale M · 4× Kh-58UShK`
- `Southeastern City · Rafale M · 8× LMUR`
- `Southeastern City · Rafale M · 2× SCALP-EG (IR · LO 0.1)`
- `Southeastern City · Rafale M · 2× SCALP-EG (INS · LO 0.1)`
- `Southeastern City · Rafale M · 2× SCALP-EG (IR · VLO 0.05)`

All sixteen loadouts carry the TALIOS pod. The five-JSOW variant uses twin racks
on the established multistore wing stations plus one centerline weapon. The
nine-JSOW variant additionally repurposes both inner wet stations for twin
racks; it is intentionally a fictional maximum-fit experiment. The surrounding
mission retains all units from Peaceful Exploration while preventing them from
attacking the player. The larger Maverick and SLAM-ER variants similarly reuse
the inner wet stations as fictional weapon stations. All five Maverick and
SLAM-ER missions start the player Rafale at 15% internal fuel, matching its
minimum-fuel load rather than the CDK's default full tanks. The three Russian
experiments also start at minimum fuel. Kh-38MT uses its infrared seeker,
Kh-58UShK is a dedicated anti-radiation experiment, and LMUR uses four twin
launchers on the same fictional wing and wet-station arrangement.

The three SCALP proxy missions share a public-data-based approximation: 1,300 kg total
mass, 5.10 m length, subsonic turbojet performance, at least 250 km nominal
range, and a roughly 450 kg two-stage BROACH penetrator warhead. The stock
AGM-84K model and guidance remain because the game does not expose a SCALP
model, TERPROM route planning, terminal scene matching, or tandem-warhead
simulation to this local mission. The 250 kg explosive fill is a deliberately
punchy gameplay approximation, not a claimed real SCALP figure; the published
450 kg figure describes the complete tandem warhead assembly. The extra blast
stands in for some BROACH precursor and penetrator damage that War Thunder's
single-stage proxy cannot reproduce.

Their reusable source index and machine-readable tuning data live in
[`assets/weapons/scalp-eg`](../../assets/weapons/scalp-eg/README.md). The
installable BLK files in this experiment remain canonical, so there is only one
copy of each definition to keep synchronized.

All three SCALP missions carry one proxy on each mirrored heavy wing station
(aircraft slots 3 and 10), matching the normal two-missile Rafale arrangement.
The custom unit inherits the complete stock `rafale_m_f3r` flight model and
changes only weapon registration and station availability. Every experiment
sets the player armada's `crewSkillK` to `1.0`, matching Gaijin player/training
missions and avoiding the baseline zero-skill pilot used by the source map.

The LO mission sets `gunnerFilterMaxDistMult` to `0.1`, matching the AGM-154A1
JSOW's current temporary SAM-AI pseudo-RCS treatment. The VLO mission sets it
to `0.05`, an intentionally fictional half-JSOW interception-distance test.
These values affect AI air-defense interception priority/range; they are not
physical radar-cross-section measurements or player-radar detection values.

The additional `INS Test` preserves the working 0.1 interception treatment but
switches the proxy to War Thunder's `sns` point-guidance path and the
`guided bombs` release channel used by the game's native coordinate-guided
stores. It is an A/B test for assigning an aiming point and launching from
behind cover without an IR vehicle lock or the targeting-optics view. Its
revised altitude schedule is 300 m while distant, 240 m on approach, 160 m
during the terminal setup, and 5 m at impact. The height controller's response
rate, acceleration gain, and maximum turn rate are deliberately reduced to
dampen the stock AGM-84K's observed vertical oscillation. War Thunder exposes
no explicit low-pass-filter setting, so this remains an approximation rather
than real TERPROM route planning. The original LO and VLO missions remain
available as known-working IR-guided baselines.

The hosted mission's 2018 formations normally depend on a multiplayer balance
rank. These local copies make the already-selected 2018 templates unconditional
so the full vehicle population also appears in `singleMission` mode.

## Install

Close War Thunder before installing, then run:

```sh
./experiments/rafale-m-f3r-loadouts/install.sh
```

Open War Thunder, choose `Battles` → `User Missions`, and start one of the
sixteen Rafale missions. The files are installed at the User Missions root using
the conventional `usr_*.mission.blk` names expected by the single-player
mission browser.

The installer also adds one isolated `wt_custom_weapons.csv` table and enables
War Thunder's `testLocalization` switch. This is required because the selected
weapon HUD derives its lookup key from each custom BLK filename; overriding
`bulletName` alone does not satisfy that lookup. The helper preserves one-time
backups of `config.blk` and `lang/localization.blk`, and it leaves every existing
localization table intact. On removal it deletes only its own table and manifest
entry; it deliberately leaves `testLocalization` enabled in case the user's
other custom text depends on it.

## Remove

```sh
./experiments/rafale-m-f3r-loadouts/uninstall.sh
```

The add-on uses only files prefixed with `wt_` and its own User Missions
subdirectory, so removal does not touch the CDK samples or the maintained
multiplayer missions.

## Experimental caveats

The weapon definitions are real game assets, but these combinations are not
registered on the stock Rafale. A weapon may function while its rack is
misaligned, or the game may reject a custom player aircraft derived from a
stock flight model. SPICE 250 is expected to be the most useful first test.
