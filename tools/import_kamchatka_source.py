#!/usr/bin/env python3
"""Materialize the official 2018 Kamchatka NE mission as a standalone BLK.

The official mission is present in the public War Thunder datamine as JSON
``.blkx`` files.  Custom Battles by URL cannot resolve those internal import
records, so this importer applies their declared categories in the same order
as the game and writes one self-contained source snapshot for our generators.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "missions" / "ne-kamchatka-2018" / "source.blk"
DATAMINE = Path("/home/adam/dev/WTFTD-War_Thunder_Full_Test_Drive/.cache/datamine")
WTFTD = Path("/home/adam/dev/WTFTD-War_Thunder_Full_Test_Drive")
MISSION = "gamedata/missions/cta/planes/nuclear_escalation/air_kamchatka_nuclear_escalation_tdm.blkx"

IMPORT_FLAGS = {
    "areas": "importAreas",
    "units": "importUnits",
    "triggers": "importTriggers",
    "mission_objectives": "importMissionObjectives",
    "wayPoints": "importWayPoints",
    "dialogs": "importDialogs",
}


def datamine_path(game_path: str) -> Path:
    """Resolve a game ``gameData/missions/*.blk`` path in the datamine."""
    relative = game_path.replace("\\", "/").lower()
    if relative.startswith("gamedata/"):
        relative = relative[len("gamedata/") :]
    if relative.endswith(".blk"):
        relative = relative[:-4] + ".blkx"
    return DATAMINE / "mis.vromfs.bin_u" / "gamedata" / relative


def as_list(value: object) -> list:
    return value if isinstance(value, list) else ([] if value is None else [value])


def merge(existing: object, incoming: object) -> object:
    """Merge imported content first, then the importing mission's content."""
    if isinstance(existing, dict) and isinstance(incoming, dict):
        result = copy.deepcopy(existing)
        for key, value in incoming.items():
            result[key] = merge(result[key], value) if key in result else copy.deepcopy(value)
        return result
    if isinstance(existing, list) and isinstance(incoming, list):
        return copy.deepcopy(existing) + copy.deepcopy(incoming)
    return copy.deepcopy(incoming)


def load(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError(f"Expected a BLK object in {path}")
    return document


def materialize(path: Path, stack: tuple[Path, ...] = ()) -> dict:
    if path in stack:
        raise ValueError(f"Circular mission import: {path}")
    document = load(path)
    result: dict = {}
    records = as_list((document.get("imports") or {}).get("import_record"))
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("file"), str):
            continue
        imported = materialize(datamine_path(record["file"]), (*stack, path))
        for category, flag in IMPORT_FLAGS.items():
            if record.get(flag, True):
                result[category] = merge(result.get(category, {}), imported.get(category, {}))

    for key, value in document.items():
        if key == "imports":
            continue
        result[key] = merge(result[key], value) if key in result else copy.deepcopy(value)
    result["imports"] = {}
    return result


def main() -> None:
    if not DATAMINE.is_dir():
        raise SystemExit(f"Datamine cache not found: {DATAMINE}")
    if not WTFTD.is_dir():
        raise SystemExit(f"WTFTD source not found: {WTFTD}")
    sys.path.insert(0, str(WTFTD))
    from wtftd import blk

    source = materialize(DATAMINE / "mis.vromfs.bin_u" / MISSION)
    groups = as_list((source.get("units") or {}).get("objectGroups"))
    if len(groups) != 108:
        raise ValueError(f"Expected 108 Kamchatka object groups, got {len(groups)}")
    if len(as_list((source.get("units") or {}).get("armada"))) != 64:
        raise ValueError("Player-unit import did not yield 64 player aircraft")
    if len(as_list((source.get("triggers") or {}).get("spawn_mlrs_01"))) != 1:
        raise ValueError("MLRS template was not imported")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(blk.dumps(source), encoding="utf-8")


if __name__ == "__main__":
    main()
