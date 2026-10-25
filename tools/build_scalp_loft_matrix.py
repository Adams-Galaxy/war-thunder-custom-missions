#!/usr/bin/env python3
"""Build the SCALP manual terminal-loft comparison matrix."""

from dataclasses import dataclass
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "rafale-m-f3r-loadouts"
WEAPONS = EXPERIMENT / "content/pkg_local/gameData/Weapons/rocketGuns"
PRESETS = EXPERIMENT / "content/pkg_local/gameData/flightModels/weaponPresets"
MISSIONS = EXPERIMENT / "UserMissions"
AIRCRAFT = EXPERIMENT / "content/pkg_local/gameData/flightModels/wt_custom_rafale_m_f3r.blk"

WEAPON_TEMPLATE = WEAPONS / "wt_agm_84k_scalp_ins_terminal_35_600_lo.blk"
WATER_MISSION_TEMPLATE = MISSIONS / "usr_wt_rafale_scalp_ins_terminal_35_600_lo2.mission.blk"
GROUND_MISSION_TEMPLATE = MISSIONS / "usr_wt_rafale_agm84k_lo2.mission.blk"


@dataclass(frozen=True)
class Variant:
    slug: str
    label: str
    mode: str
    range_map: tuple[float, float, float, float] | None = None
    loft_target_elevation_deg: float = -65.0
    loft_angle_gain: float = 0.75
    altitude_points: tuple[tuple[float, float], ...] = ()

    @property
    def weapon_stem(self) -> str:
        return f"wt_agm_84k_scalp_loft_{self.slug}_lo"

    @property
    def loadout(self) -> str:
        return f"wt_rafale_m_scalp_loft_{self.slug}_lo2"

    @property
    def station_stem(self) -> str:
        return f"wt_scalp_loft_{self.slug}_lo"

    @property
    def water_mission(self) -> Path:
        return MISSIONS / f"usr_wt_rafale_scalp_loft_{self.slug}_water_lo2.mission.blk"

    @property
    def ground_mission(self) -> Path:
        return MISSIONS / f"usr_wt_rafale_scalp_loft_{self.slug}_ground_lo2.mission.blk"


def manual_variant(lead_s: float, altitude_m: float) -> Variant:
    lead_slug = f"{lead_s:.1f}".replace(".", "")
    return Variant(
        f"manual{lead_slug}_{altitude_m:.0f}",
        f"Manual Loft {lead_s:.1f} s · {altitude_m:.0f} m",
        "altitude_hold",
        altitude_points=(
            (0.0, altitude_m),
            (lead_s, altitude_m),
            (lead_s + 0.25, 35.0),
            (8.0, 35.0),
            (8.5, 80.0),
        ),
    )


VARIANTS = tuple(
    manual_variant(lead_s, altitude_m)
    for lead_s in (2.0, 1.5, 1.0)
    for altitude_m in (600.0, 1000.0)
)


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected one occurrence of {old!r}, found {text.count(old)}")
    return text.replace(old, new, 1)


def weapon_text(variant: Variant) -> str:
    text = WEAPON_TEMPLATE.read_text()
    _, rest = text.split("\n", 1)
    text = f"// SCALP comparison experiment: {variant.label}.\n" + rest

    # Every altitude-hold comparison uses the same damping that behaved well in game.
    text = replace_once(text, "altitudeHoldTargetOmegaMax:r=1.05", "altitudeHoldTargetOmegaMax:r=0.95")
    text = replace_once(text, "altitudeRateRateToClimb:r=0.15", "altitudeRateRateToClimb:r=0.135")
    text = replace_once(text, "climbDiffToAccelMult:r=0.016", "climbDiffToAccelMult:r=0.0125")

    if variant.mode == "range_loft":
        assert variant.range_map is not None
        near_range, near_angle, far_range, far_angle = variant.range_map
        text = replace_once(text, '"@override:loftEnabled":b=no', '"@override:loftEnabled":b=yes')
        loft = (
            f"      rangeToLoftElevation:p4={near_range:g}, {near_angle:g}, {far_range:g}, {far_angle:g}\n"
            f"      loftTargetElevation:r={variant.loft_target_elevation_deg:g}\n"
            f"      loftAngleToAccelMult:r={variant.loft_angle_gain:g}\n"
            "      loftTargetOmegaMax:r=0.95"
        )
        text = replace_once(text, "      altitudeHoldEnabled:b=yes", loft + "\n      altitudeHoldEnabled:b=no")
        text = re.sub(r"^\s*timeToHitToAltitude[0-4]:p2=.*\n", "", text, flags=re.MULTILINE)
        text = re.sub(
            r"^\s*(?:altitudeHoldTargetElevation|altitudeHoldTargetOmegaMax|altitudeDiffToClimb|altitudeRateRateToClimb|climbDiffToAccelMult):r=.*\n",
            "",
            text,
            flags=re.MULTILINE,
        )
        text = re.sub(r"^\s*altitudeHoldAngleLimith:p2=.*\n", "", text, flags=re.MULTILINE)
    else:
        text = re.sub(r"^\s*timeToHitToAltitude[0-4]:p2=.*\n", "", text, flags=re.MULTILINE)
        point_lines = "\n".join(
            f"      timeToHitToAltitude{idx}:p2={time_s:g}, {altitude_m:g}"
            for idx, (time_s, altitude_m) in enumerate(variant.altitude_points)
        )
        text = replace_once(text, "      altitudeHoldEnabled:b=yes", "      altitudeHoldEnabled:b=yes\n" + point_lines)
        text = replace_once(text, "altitudeHoldAngleLimith:p2=-82.0, 78.0", "altitudeHoldAngleLimith:p2=-82.0, 70.0")
    return text


def preset_text(variant: Variant) -> str:
    return f'''Weapon {{
  slot:i=3
  preset:t="{variant.station_stem}_slot3"
}}
Weapon {{
  slot:i=6
  preset:t="damocles"
}}
Weapon {{
  slot:i=10
  preset:t="{variant.station_stem}_slot10"
}}
'''


def mission_text(template: Path, variant: Variant, ground: bool) -> str:
    text = template.read_text()
    original_loadout = "wt_rafale_m_agm84k_lo2" if ground else "wt_rafale_m_scalp_ins_terminal_35_600_lo2"
    text = text.replace(original_loadout, variant.loadout)
    if not ground:
        text = replace_once(text, "[40000.0, 1500.0, -52000.0]", "[40000.0, 100.0, -52000.0]")
    range_label = "Ground" if ground else "Water"
    text = re.sub(
        r'^    locName:t=".*"$',
        f'    locName:t="Southeastern City · SCALP Test · {variant.label} · {range_label}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    location = "NATO Air Spawn 1 at 1.5 km" if ground else "100 m over the flat-water range"
    if variant.mode == "range_loft":
        assert variant.range_map is not None
        near_range, near_angle, far_range, far_angle = variant.range_map
        description = (
            f"Native loft-only range-map test, starting {location}. The map requests {far_angle:g} degrees "
            f"at {far_range / 1000:g} km and {near_angle:g} degrees at {near_range / 1000:g} km. "
            "This tests whether War Thunder recalculates the loft angle during flight or samples launch range once."
        )
    else:
        lead_s, demanded_altitude = variant.altitude_points[1]
        description = (
            f"Manual altitude-hold loft test, starting {location}. It cruises at 80 m, descends to 35 m, "
            f"then reaches a {demanded_altitude:g} m command at {lead_s:g} seconds to impact through a "
            "0.25-second transition. The same high command is retained through zero seconds; there is no "
            "return-to-target altitude keyframe, so terminal target-elevation guidance must complete the dive."
        )
    return re.sub(
        r'^    locDesc:t=".*"$',
        f'    locDesc:t="{description}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )


def preset_registration(variant: Variant) -> str:
    return f'''  preset {{
    name:t="{variant.loadout}"
    blk:t="gameData/flightModels/weaponPresets/{variant.loadout}.blk"
    weaponConfig {{
      presetType:t="AIR_TO_GROUND"
      Weapon {{
        blk:t="gameData/Weapons/rocketGuns/{variant.weapon_stem}.blk"
        iconType:t="glide_bomb_default"
        amountPerTier:r=1.0
        tier {{ idx:i=10 }}
        tier {{ idx:i=2 }}
      }}
    }}
  }}'''


def station_registration(variant: Variant, slot: int) -> str:
    node = "pylon_pu_708_001" if slot == 3 else "pylon_pu_708_002"
    emitter = "pylon_at_730_001" if slot == 3 else "pylon_at_730_002"
    return f'''    WeaponPreset {{
      iconType:t="glide_bomb_default"
      name:t="{variant.station_stem}_slot{slot}"
      ShowNodes {{
        node:t="{node}"
      }}
      Weapon {{
        trigger:t="atgm"
        blk:t="gameData/Weapons/rocketGuns/{variant.weapon_stem}.blk"
        emitter:t="{emitter}"
        bullets:i=1
        external:b=yes
        separate:b=yes
        machLimit:r=1.4
      }}
    }}'''


def replace_generated_region(text: str, label: str, body: str, anchor: str) -> str:
    start = f"// BEGIN GENERATED {label}"
    end = f"// END GENERATED {label}"
    region = f"{start}\n{body}\n{end}"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.DOTALL)
    if pattern.search(text):
        return pattern.sub(region, text, count=1)
    if text.count(anchor) != 1:
        raise ValueError(f"Expected one insertion anchor for {label}")
    return text.replace(anchor, region + "\n" + anchor, 1)


def update_aircraft() -> None:
    text = AIRCRAFT.read_text()
    text = replace_generated_region(
        text,
        "SCALP LOFT MATRIX PRESETS",
        "\n".join(preset_registration(v) for v in VARIANTS),
        "// BEGIN GENERATED SCALP TERMINAL MATRIX PRESETS",
    )
    for slot in (3, 10):
        text = replace_generated_region(
            text,
            f"SCALP LOFT MATRIX SLOT {slot}",
            "\n\n".join(station_registration(v, slot) for v in VARIANTS),
            f"// BEGIN GENERATED SCALP TERMINAL MATRIX SLOT {slot}",
        )
    AIRCRAFT.write_text(text)


def main() -> None:
    for variant in VARIANTS:
        (WEAPONS / f"{variant.weapon_stem}.blk").write_text(weapon_text(variant))
        (PRESETS / f"{variant.loadout}.blk").write_text(preset_text(variant))
        variant.water_mission.write_text(mission_text(WATER_MISSION_TEMPLATE, variant, False))
        variant.ground_mission.write_text(mission_text(GROUND_MISSION_TEMPLATE, variant, True))
    update_aircraft()


if __name__ == "__main__":
    main()
