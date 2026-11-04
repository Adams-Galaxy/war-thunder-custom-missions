#!/usr/bin/env python3
"""Build Poland · Forrestal Lake from the live client's official Poland TDM.

This deliberately starts with the actual self-contained Poland mission rather
than attempting to hand-author a custom-room shell.  The carrier is the only
gameplay addition.
"""

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "missions/poland-nimitz-lake/poland-nimitz-lake.blk"
GAME = Path("/games/SteamLibrary/steamapps/common/War Thunder")
WTFTD = Path("/home/adam/dev/WTFTD-War_Thunder_Full_Test_Drive")
OFFICIAL_POLAND_TDM = "gamedata/missions/cta/tanks/poland/poland_tdm.blk"


def main() -> None:
    if not (WTFTD / "wtftd").is_dir():
        raise SystemExit("WTFTD source is required to decode the installed official mission")
    sys.path.insert(0, str(WTFTD))
    from wtftd import blk, vromfs

    mission = vromfs.Container(GAME / "mis.vromfs.bin").blk(OFFICIAL_POLAND_TDM)
    settings = mission["mission_settings"]["mission"]
    settings["locName"] = "Poland · Forrestal Lake"
    settings["locDesc"] = "Normal Poland Tank Deathmatch with a stationary USS Forrestal in the central lake."
    settings.setdefault("allowedUnitTypes", {})["isShipsAllowed"] = True

    carrier = {
        "name": "us_forrestal_lake",
        "tm": [[0.0, 0.0, -1.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0], [2018.0, 0.0, 2037.0]],
        "unit_class": "us_aircraftcarrier_forrestal_ai",
        "objLayer": 1,
        "closed_waypoints": False,
        "isShipSpline": False,
        "shipTurnRadius": 300.0,
        "weapons": "",
        "bullets0": "", "bullets1": "", "bullets2": "", "bullets3": "",
        "bulletsCount0": 0, "bulletsCount1": 0, "bulletsCount2": 0, "bulletsCount3": 0,
        "crewSkillK": 1.0,
        "applyAllMods": True,
        "props": {"army": 1, "count": 1, "formation_type": "rows", "formation_div": 3,
                  "formation_step": [2.5, 2.0], "formation_noise": [0.1, 0.1]},
        "way": {},
    }
    units = mission.setdefault("units", {})
    ships = units.get("ships")
    units["ships"] = [ships, carrier] if isinstance(ships, dict) else (ships or []) + [carrier]

    # The source mission already has proven tank spawns. Add an optional Team
    # A carrier takeoff slot using the same complete respawn-action structure.
    actions = mission["triggers"]["mission_init_both"]["actions"]
    marks = actions["missionMarkAsRespawnPoint"]
    marks.append({"loc_name": "USS Forrestal · Lake", "spawnEffect": False,
                  "isStrictSpawn": False, "isAirfield": True, "isUnit": False,
                  "useExisting": False, "isIndividual": True, "removeAreas": False,
                  "canSpawnOnNeutral": False, "showOnMap": True, "radius": -1.0,
                  "onlyOnePlayerPerSpawnPoint": False, "separate_fuel_time": False,
                  "modular_airfield": False, "target": "us_forrestal_lake", "team": "A",
                  "offset": [0.0, 0.0, 0.0], "tags": {"carrier_take_off": True}})

    OUT.write_text("// Generated from the installed official Poland TDM mission.\n" + blk.dumps(mission), encoding="utf-8")


if __name__ == "__main__":
    main()
