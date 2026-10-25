#!/usr/bin/env python3
"""Build the controlled SCALP terminal-turn test matrix."""

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
MISSION_TEMPLATE = MISSIONS / "usr_wt_rafale_scalp_ins_terminal_35_600_lo2.mission.blk"
GROUND_MISSION_TEMPLATE = MISSIONS / "usr_wt_rafale_agm84k_lo2.mission.blk"


@dataclass(frozen=True)
class Variant:
    slug: str
    turnover_s: float
    climb_cap_deg: float
    climb_gain: float = 0.016
    target_omega_max: float = 1.05
    altitude_rate_gain: float = 0.15

    @property
    def apex_command_s(self) -> float:
        return self.turnover_s + 0.25

    @property
    def timing_label(self) -> str:
        if (self.turnover_s * 10).is_integer():
            return f"{self.turnover_s:.1f}"
        return f"{self.turnover_s:.2f}"

    @property
    def weapon_stem(self) -> str:
        return f"wt_agm_84k_scalp_turn_{self.slug}_lo"

    @property
    def loadout(self) -> str:
        return f"wt_rafale_m_scalp_turn_{self.slug}_lo2"

    @property
    def station_stem(self) -> str:
        return f"wt_scalp_turn_{self.slug}_lo"

    @property
    def mission_stem(self) -> str:
        return f"usr_wt_rafale_scalp_turn_{self.slug}_lo2.mission"

    @property
    def display_suffix(self) -> str:
        suffix = f"Turn {self.timing_label}s · {self.climb_cap_deg:.0f}°"
        if self.climb_gain != 0.016:
            suffix += " · Soft Gain"
        return suffix


VARIANTS = (
    Variant("lead20_cap55", 2.0, 55.0),
    Variant("lead25_cap55", 2.5, 55.0),
    Variant("lead30_cap55", 3.0, 55.0),
    Variant("lead25_cap45", 2.5, 45.0),
    Variant("lead25_cap35", 2.5, 35.0),
    Variant("lead25_cap45_gain0125", 2.5, 45.0, 0.0125),
    Variant("lead20_cap45_gain0125", 2.0, 45.0, 0.0125),
    Variant("lead175_cap45_gain0125", 1.75, 45.0, 0.0125),
    Variant("lead15_cap45_gain0125", 1.5, 45.0, 0.0125),
    Variant("lead125_cap45_gain0125_damped", 1.25, 45.0, 0.0125, 0.95, 0.135),
    Variant("lead10_cap45_gain0125_damped", 1.0, 45.0, 0.0125, 0.95, 0.135),
    Variant("lead075_cap45_gain0125_damped", 0.75, 45.0, 0.0125, 0.95, 0.135),
)

GROUND_VARIANT_SLUG = "lead10_cap45_gain0125_damped"
GROUND_MISSION = MISSIONS / "usr_wt_rafale_scalp_turn_lead10_cap45_gain0125_damped_ground_lo2.mission.blk"


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected one occurrence of {old!r}, found {text.count(old)}")
    return text.replace(old, new, 1)


def weapon_text(variant: Variant) -> str:
    text = WEAPON_TEMPLATE.read_text()
    first_line, rest = text.split("\n", 1)
    text = (
        f"// SCALP terminal matrix: 600 m command, descent led by "
        f"{variant.timing_label} s, climb capped at {variant.climb_cap_deg:.0f} degrees.\n"
        + rest
    )
    text = replace_once(text, "timeToHitToAltitude0:p2=0.95, 5.0", f"timeToHitToAltitude0:p2={variant.turnover_s:.2f}, 5.0")
    text = replace_once(text, "timeToHitToAltitude1:p2=1.20, 600.0", f"timeToHitToAltitude1:p2={variant.apex_command_s:.2f}, 600.0")
    text = replace_once(text, "timeToHitToAltitude2:p2=5.0, 35.0", "timeToHitToAltitude2:p2=6.0, 35.0")
    text = replace_once(text, "altitudeHoldTargetOmegaMax:r=1.05", f"altitudeHoldTargetOmegaMax:r={variant.target_omega_max:g}")
    text = replace_once(text, "altitudeRateRateToClimb:r=0.15", f"altitudeRateRateToClimb:r={variant.altitude_rate_gain:g}")
    text = replace_once(text, "climbDiffToAccelMult:r=0.016", f"climbDiffToAccelMult:r={variant.climb_gain:g}")
    text = replace_once(text, "altitudeHoldAngleLimith:p2=-82.0, 78.0", f"altitudeHoldAngleLimith:p2=-82.0, {variant.climb_cap_deg:.1f}")
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


def mission_text(variant: Variant) -> str:
    text = MISSION_TEMPLATE.read_text().replace(
        "wt_rafale_m_scalp_ins_terminal_35_600_lo2", variant.loadout
    )
    text = replace_once(
        text,
        "[40000.0, 1500.0, -52000.0]",
        "[40000.0, 100.0, -52000.0]",
    )
    text = re.sub(
        r'^    locName:t=".*"$',
        f'    locName:t="Southeastern City · Rafale M · SCALP {variant.display_suffix}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    description = (
        "Flat-water terminal-turn matrix. Medium damping, 35 m low approach, "
        f"600 m apex command, descent commanded {variant.timing_label} seconds before impact, "
        f"and climb angle capped at {variant.climb_cap_deg:.0f} degrees. "
        f"Climb gain is {variant.climb_gain:g}. The player spawns at 100 m facing between "
        "two stationary targets exactly 12 km away."
    )
    text = re.sub(
        r'^    locDesc:t=".*"$',
        f'    locDesc:t="{description}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    return text


def ground_mission_text(variant: Variant) -> str:
    text = GROUND_MISSION_TEMPLATE.read_text().replace(
        "wt_rafale_m_agm84k_lo2", variant.loadout
    )
    text = re.sub(
        r'^    locName:t=".*"$',
        f'    locName:t="Southeastern City · Rafale M · SCALP Ground · {variant.display_suffix}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    description = (
        "Ground-range terminal test using the 1.0-second softened and slightly more damped profile. "
        "The Rafale starts at NATO Air Spawn 1 at 1.5 km, facing west across the ground target area."
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
    preset_body = "\n".join(preset_registration(v) for v in VARIANTS)
    text = replace_generated_region(
        text,
        "SCALP TERMINAL MATRIX PRESETS",
        preset_body,
        '  preset {\n    name:t="wt_rafale_m_scalp_ins_ultralate_medium_lo2"',
    )
    for slot, anchor in (
        (3, '    WeaponPreset {\n      iconType:t="glide_bomb_default"\n      name:t="wt_scalp_ins_ultralate_medium_lo_slot3"'),
        (10, '    WeaponPreset {\n      iconType:t="glide_bomb_default"\n      name:t="wt_scalp_ins_ultralate_medium_lo_slot10"'),
    ):
        body = "\n\n".join(station_registration(v, slot) for v in VARIANTS)
        text = replace_generated_region(
            text, f"SCALP TERMINAL MATRIX SLOT {slot}", body, anchor
        )
    AIRCRAFT.write_text(text)


def main() -> None:
    for variant in VARIANTS:
        (WEAPONS / f"{variant.weapon_stem}.blk").write_text(weapon_text(variant))
        (PRESETS / f"{variant.loadout}.blk").write_text(preset_text(variant))
        (MISSIONS / f"{variant.mission_stem}.blk").write_text(mission_text(variant))
    ground_variant = next(v for v in VARIANTS if v.slug == GROUND_VARIANT_SLUG)
    GROUND_MISSION.write_text(ground_mission_text(ground_variant))
    update_aircraft()


if __name__ == "__main__":
    main()
