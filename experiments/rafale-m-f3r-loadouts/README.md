# Rafale M F3-R local weapon experiments

This is an intentionally local, single-player-only experiment built on the
peaceful South-Eastern City mission. It does not alter the stock Rafale or any
hosted multiplayer mission.

The package adds one custom unit based on `rafale_m_f3r` and five missions:

- `Southeastern City · Rafale M · 8× SPICE 250`
- `Southeastern City · Rafale M · 6× Brimstone DM`
- `Southeastern City · Rafale M · 2× AGM-154A1 JSOW`
- `Southeastern City · Rafale M · 5× AGM-154A1 JSOW`
- `Southeastern City · Rafale M · 9× AGM-154A1 JSOW`

All five loadouts carry the TALIOS pod. The five-JSOW variant uses twin racks
on the established multistore wing stations plus one centerline weapon. The
nine-JSOW variant additionally repurposes both inner wet stations for twin
racks; it is intentionally a fictional maximum-fit experiment. The surrounding
mission retains all units from Peaceful Exploration while preventing them from
attacking the player.

The hosted mission's 2018 formations normally depend on a multiplayer balance
rank. These local copies make the already-selected 2018 templates unconditional
so the full vehicle population also appears in `singleMission` mode.

## Install

Close War Thunder before installing, then run:

```sh
./experiments/rafale-m-f3r-loadouts/install.sh
```

Open War Thunder, choose `Battles` → `User Missions`, and start one of the
five Rafale missions. The files are installed at the User Missions root using
the conventional `usr_*.mission.blk` names expected by the single-player
mission browser.

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
