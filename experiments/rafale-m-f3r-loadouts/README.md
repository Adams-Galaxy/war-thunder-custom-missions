# Rafale M F3-R local weapon experiments

This is an intentionally local, single-player-only experiment built on the
peaceful South-Eastern City mission. It does not alter the stock Rafale or any
hosted multiplayer mission.

The package adds one custom unit based on `rafale_m_f3r` and twenty-four missions:

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
- `Southeastern City · Rafale M · SCALP 5s 35→600`
- `Southeastern City · Rafale M · SCALP 5s 40→1000`
- `Southeastern City · Rafale M · SCALP Water Reference`
- `Southeastern City · Rafale M · SCALP Turn 2.0s · 55°`
- `Southeastern City · Rafale M · SCALP Turn 2.5s · 55°`
- `Southeastern City · Rafale M · SCALP Turn 3.0s · 55°`
- `Southeastern City · Rafale M · SCALP Turn 2.5s · 45°`
- `Southeastern City · Rafale M · SCALP Turn 2.5s · 35°`
- `Southeastern City · Rafale M · SCALP Turn 2.5s · 45° · Soft Gain`
- `Southeastern City · Rafale M · 2× SCALP-EG (IR · VLO 0.05)`

All twenty-four loadouts carry the TALIOS pod. The five-JSOW variant uses twin racks
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

The five SCALP proxy missions share a public-data-based approximation: 1,300 kg total
mass, 5.10 m length, subsonic turbojet performance, at least 250 km nominal
range, and a roughly 450 kg two-stage BROACH penetrator warhead. All three use
the stock AGM-84K visual and reconstructed aerodynamics because the game does
not expose a SCALP model, TERPROM route planning, terminal scene matching, or
tandem-warhead simulation to this local mission. The two IR variants retain the
AGM-84K optical guidance. The INS experiment instead inherits the seekerless
SNS guidance path from Grom-1, with its boost stage disabled and the SCALP
flight values restored explicitly. The 250 kg explosive fill is a deliberately
punchy gameplay approximation, not a claimed real SCALP figure; the published
450 kg figure describes the complete tandem warhead assembly. The extra blast
stands in for some BROACH precursor and penetrator damage that War Thunder's
single-stage proxy cannot reproduce.

Their reusable source index and machine-readable tuning data live in
[`assets/weapons/scalp-eg`](../../assets/weapons/scalp-eg/README.md). The
installable BLK files in this experiment remain canonical, so there is only one
copy of each definition to keep synchronized.

All five SCALP missions carry one proxy on each mirrored heavy wing station
(aircraft slots 3 and 10), matching the normal two-missile Rafale arrangement.
The custom unit inherits the complete stock `rafale_m_f3r` flight model and
changes only weapon registration and station availability. Every experiment
sets the player armada's `crewSkillK` to `1.0`, matching Gaijin player/training
missions and avoiding the baseline zero-skill pilot used by the source map.
Every mission also starts the Rafale at the map's NATO Air Spawn 1, 1,500 m
above the western forward airfield, rather than at the original mission start.

The LO mission sets `gunnerFilterMaxDistMult` to `0.1`, matching the AGM-154A1
JSOW's current temporary SAM-AI pseudo-RCS treatment. The VLO mission sets it
to `0.05`, an intentionally fictional half-JSOW interception-distance test.
These values affect AI air-defense interception priority/range; they are not
physical radar-cross-section measurements or player-radar detection values.

The three `INS` terminal tests preserve the working 0.1 interception treatment but
use War Thunder's seekerless Grom-1 `sns` point-guidance path. They return to
the missile/ATGM release channel so the unwanted guided-bomb CCRP symbology is
not shown. All now use the proven medium damping. Test A is the known-good
ultra-late 25-to-260 m reference. Test B holds a 35 m terminal approach until
five seconds to impact, then gives the controller time to climb toward 600 m.
Test C uses the same five-second start but deliberately commands a 1,000 m
apex from 40 m, testing whether a large altitude error overcomes the damping.
Both profiles now compress the apex-to-near-ground command into 0.25 seconds,
so the controller should reverse directly from its climb into the dive instead
of spending roughly a second in a shallow, nearly level transition.
The extra
altitude keyframe is supported by stock War Thunder missile definitions and
prevents the pop-up from being smeared into one long shallow climb. The listed distances are rough
time-to-impact estimates, not fixed map distances. War Thunder exposes no
explicit low-pass-filter setting, so this remains an approximation rather than
real TERPROM route planning. The original LO and VLO missions remain available
as known-working IR-guided baselines.

All three INS weapon files directly include the stock Grom-1 definition. An
earlier attempt to make tests B and C include test A's custom `pkg_local` BLK
caused repeatable fatal game crashes, so the variants are intentionally
standalone despite the duplicated base tuning.

All three terminal-profile missions use the same flat-water test range. The
Rafale starts at `(40000, 1500, -52000)` and two unarmed stationary destroyers sit
exactly 12 km away at the other corners of an equilateral triangle. This removes
terrain-height ambiguity and gives one target per missile.

Twelve terminal-turn definitions form a controlled tuning matrix. The current
playable set is the 1.25, 1.0, and 0.75-second water tests plus a 1.0-second
ground-range mission; older mission files remain in Git as reference material
but are removed from the active User Missions folder during this tuning pass. They
spawn the Rafale at 100 m over water, with its identity transform pointing at
the midpoint between the two ships. All use the same 35 m low approach, 600 m
apex command, medium damping, and 0.25-second
apex-to-descent command transition. Three command the descent 2.0, 2.5, or 3.0
seconds before impact with a 55-degree climb cap. Two hold the 2.5-second timing
while lowering the cap to 45 or 35 degrees. Four softened 45-degree profiles use
a climb gain of 0.0125 and command descent at 2.5, 2.0, 1.75, or 1.5 seconds
before impact. Three further profiles tighten that to 1.25, 1.0, and 0.75
seconds while slightly lowering target omega from 1.05 to 0.95 and vertical-rate
gain from 0.15 to 0.135. The 1.0-second ground mission starts at NATO Air Spawn
1 at 1.5 km, using the established west-facing transform. Regenerate this matrix with
`python tools/build_scalp_terminal_matrix.py` after changing its variant table.

Because the INS version inherits Grom-1 only to obtain its seekerless SNS
guidance path, it explicitly replaces Grom's solid-rocket flame, smoke, and
haze with the AGM-84K's long-burn turbojet-style exhaust presentation. The
thrust schedule remains the existing mass-scaled SCALP approximation.

The hosted mission's 2018 formations normally depend on a multiplayer balance
rank. These local copies make the already-selected 2018 templates unconditional
so the full vehicle population also appears in `singleMission` mode.

## Install

Close War Thunder before installing, then run:

```sh
./experiments/rafale-m-f3r-loadouts/install.sh
```

Open War Thunder, choose `Battles` → `User Missions`, and start one of the
eighteen Rafale missions. The files are installed at the User Missions root using
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
