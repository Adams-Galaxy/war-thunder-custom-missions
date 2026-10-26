#!/usr/bin/env python3
"""Build the active South-Eastern City Rafale war-zone practice mission."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "missions/ne-southeastern-city/normal.blk"
REFERENCE = (
    ROOT
    / "experiments/rafale-m-f3r-loadouts/UserMissions"
    / "usr_wt_rafale_kh38mt4.mission.blk"
)
OUTPUT = (
    ROOT
    / "experiments/rafale-m-f3r-loadouts/UserMissions"
    / "usr_wt_rafale_warzone_practice.mission.blk"
)


def block_end(text: str, start: int) -> int:
    open_brace = text.index("{", start)
    depth = 0
    for index in range(open_brace, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("unterminated BLK block")


def named_armada(text: str, name: str) -> tuple[int, int]:
    name_at = text.index(f'name:t="{name}"')
    start = text.rfind("  armada{", 0, name_at)
    if start < 0:
        raise ValueError(f"armada {name!r} not found")
    return start, block_end(text, start)


def replace_named_block(text: str, block_name: str, replacement: str) -> str:
    start = text.index(f"  {block_name}{{")
    end = block_end(text, start)
    return text[:start] + replacement + text[end:]


def armada(
    name: str,
    unit_class: str,
    weapons: str,
    army: int,
    count: int,
    position: tuple[float, float, float],
    attack_type: str,
    task: str,
    *,
    protected_from_ai: bool = False,
    speed: float = 0.0,
) -> str:
    x, y, z = position
    protection = "\n      targetableByAi:b=no" if protected_from_ai else ""
    speed_line = f"\n      speed:r={speed:.1f}" if speed else ""
    return f'''  armada{{
    name:t="{name}"
    tm:m=[[1.0, 0.0, 0.0] [0.0, 1.0, 0.0] [0.0, 0.0, 1.0] [{x:.3f}, {y:.3f}, {z:.3f}]]
    unit_class:t="{unit_class}"
    closed_waypoints:b=no
    isShipSpline:b=no
    shipTurnRadius:r=100.0
    weapons:t="{weapons}"
    fuel:r=100.0
    bullets0:t=""
    bullets1:t=""
    bullets2:t=""
    bullets3:t=""
    bulletsCount0:i=0
    bulletsCount1:i=0
    bulletsCount2:i=0
    bulletsCount3:i=0
    crewSkillK:r=1.0
    applyAllMods:b=yes
    props{{
      army:i={army}
      count:i={count}
      numInWing:i=2
      free_distance:r=180.0
      floating_distance:r=100.0
      minimum_distance_to_earth:r=20.0
      altLimit:r=10000.0
      attack_type:t="{attack_type}"
      canLeaveRouteForAtack:b=yes
      targetAir:b={'yes' if task == 'ATTACK_AIR' else 'no'}
      targetGnd:b={'yes' if task == 'ATTACK_GROUND' else 'no'}
      isDelayed:b=yes
      skill:i=4{protection}{speed_line}
      plane{{
        wing_formation:t="Echelon"
        row_distances:r=8.0
        col_distances:r=8.0
        super_formation:t="Echelon"
        super_row_distances:r=4.0
        super_col_distances:r=4.0
        ai_skill:t="ACE"
        aggressiveWingman:b=yes
        task:t="{task}"
      }}
    }}
    way{{
    }}
  }}'''


def attack_action(
    object_name: str,
    attack_type: str,
    target_type: str,
    *,
    player_attracted: bool = False,
    weapon_type: str = "all",
    target: str | None = None,
) -> str:
    attracted = "\n        playerAttracted:b=yes\n        playerAttractedCount:i=4" if player_attracted else ""
    target_line = f'\n        target:t="{target}"' if target else ""
    return f'''      unitAttackTarget{{
        object:t="{object_name}"
        attack_type:t="{attack_type}"{target_line}
        targetTypeName:t="{target_type}"
        targetDistMax:r=65000.0{attracted}
        fightInArea:t="battlearea"
        fightAreaRadius:r=52000.0
        fightAreaOuterRadius:r=60000.0
        weaponType:t="{weapon_type}"
        groupAttackMode:t="wing"
      }}'''


def warzone_trigger(
    name: str,
    units: list[tuple[str, str, str, bool, str, bool, str | None]],
    delay: float | None,
) -> str:
    if delay is None:
        events = "      initMission{\n\n      }"
        conditions = ""
    else:
        events = "      periodicEvent{\n        time:r=1.0\n      }"
        conditions = f'''      missionWhenTime{{
        value:r={delay:.1f}
      }}'''
    actions: list[str] = []
    for unit, attack_type, target_type, attracted, weapon_type, protected, target in units:
        if protected:
            actions.append(f'''      unitSetProperties{{
        object:t="{unit}"
        targetableByAi:b=no
      }}''')
        actions.append(f'''      unitWakeUp{{
        target:t="{unit}"
      }}''')
        actions.append(
            attack_action(
                unit,
                attack_type,
                target_type,
                player_attracted=attracted,
                weapon_type=weapon_type,
                target=target,
            )
        )
    return f'''  {name}{{
    is_enabled:b=yes
    comments:t="Staggered war-zone air package. Low strike groups remain manually targetable but are hidden from AI SPAA."
    props{{
      actionsType:t="PERFORM_ONE_BY_ONE"
      conditionsType:t="ALL"
      enableAfterComplete:b=no
    }}
    events{{
{events}
    }}
    conditions{{
{conditions}
    }}
    actions{{
{chr(10).join(actions)}
    }}
    else_actions{{

    }}
  }}'''


def ai_targeting_window_trigger(
    name: str, units: tuple[str, ...], mission_time: float, targetable: bool
) -> str:
    state = "yes" if targetable else "no"
    actions = "\n".join(
        f'''      unitSetProperties{{
        object:t="{unit}"
        targetableByAi:b={state}
      }}'''
        for unit in units
    )
    return f'''  {name}{{
    is_enabled:b=yes
    comments:t="Open or close a short AI-SPAA engagement window for low strike packages."
    props{{
      actionsType:t="PERFORM_ONE_BY_ONE"
      conditionsType:t="ALL"
      enableAfterComplete:b=no
    }}
    events{{
      periodicEvent{{
        time:r=1.0
      }}
    }}
    conditions{{
      missionWhenTime{{
        value:r={mission_time:.1f}
      }}
    }}
    actions{{
{actions}
    }}
    else_actions{{

    }}
  }}'''


def build() -> str:
    text = SOURCE.read_text()

    player_start = text.index("  player{")
    mission_start = text.index("  mission{", player_start)
    text = text[:player_start] + '  player{\n    army:i=2\n    wing:t="t2_player01"\n  }\n' + text[mission_start:]
    text = text.replace(
        '    type:t="domination"',
        '    name:t="wt_rafale_warzone_practice"\n    type:t="singleMission"',
        1,
    )
    text = text.replace("    afterRespawnDelaySec:i=480", "    afterRespawnDelaySec:i=1", 1)
    text = text.replace(
        '    locName:t="Nuclear Escalation · Southeastern City [NORMAL]"',
        '    locName:t="Southeastern City · Rafale War-Zone Practice"',
        1,
    )
    text = text.replace(
        '    locDesc:t="Custom version of the official Nuclear Escalation mission. Stars mark Soviet-aligned air defenses; crosses mark NATO. All strategic and airfield defenses retain their stock behavior."',
        '    locDesc:t="Full-combat practice over the stock Nuclear Escalation battle. Strategic and short-range air defenses remain active. Enemy Su-30SM2 and MiG-35 fighters contest the sky while Russian and NATO strike packages attack the ground war. Player respawns, fuel, ammunition, and airborne rearm are unlimited."',
        1,
    )
    text = text.replace(
        "    deathPenaltyMul:r=0.2",
        "    deathPenaltyMul:r=0.2\n    maxRespawns:i=-1\n    respawnTimeMultiplier:r=0.1\n    allowEmptyTeams:b=yes\n    isLimitedFuel:b=no\n    isLimitedAmmo:b=no",
        1,
    )
    text = text.replace("      isHelicoptersAllowed:b=no", "      isHelicoptersAllowed:b=yes", 1)

    support_trigger = '''  practice_player_support{
    is_enabled:b=yes
    comments:t="Wake the player and accelerate Arcade airborne rearm without protection or forced speed."
    props{
      actionsType:t="PERFORM_ONE_BY_ONE"
      conditionsType:t="ALL"
      enableAfterComplete:b=yes
    }
    events{
      periodicEvent{
        time:r=1.0
      }
    }
    conditions{

    }
    actions{
      unitWakeUp{
        target:t="t2_player01"
      }
      unitForceRearmSpeed{
        target:t="t2_player01"
        rearmSpeedK:r=80.0
      }
    }
    else_actions{

    }
  }'''
    text = replace_named_block(text, "debug_in_single", support_trigger)
    text = text.replace("  debug_in_multiplayer{\n    is_enabled:b=yes", "  debug_in_multiplayer{\n    is_enabled:b=no", 1)

    initial_units = [
        ("war_t1_su30_hunters_a", "attack_player_B", "airplane", True, "all", False, None),
        ("war_t1_su25_rockets_a", "attack_target", "surface", False, "rockets", True, "t2_base_02"),
        ("war_t1_ka52_attack_a", "attack_target", "surface", False, "all", True, "t2_strongpoint_02"),
        ("war_t2_rafale_cap_a", "fire_at_will_air", "airplane", False, "all", False, None),
        ("war_t2_a10_rockets_a", "attack_target", "surface", False, "rockets", True, "t1_base_03"),
    ]
    second_units = [
        ("war_t1_su30_hunters_b", "attack_player_B", "airplane", True, "all", False, None),
        ("war_t1_mig35_cap_a", "fire_at_will_air", "airplane", False, "all", False, None),
        ("war_t1_su34_strike", "attack_target", "surface", False, "rockets", True, "t2_base_03"),
        ("war_t2_rafale_cap_b", "fire_at_will_air", "airplane", False, "all", False, None),
        ("war_t2_f15e_strike", "attack_target", "surface", False, "all", True, "t1_base_02"),
    ]
    third_units = [
        ("war_t1_mig35_cap_b", "fire_at_will_air", "airplane", False, "all", False, None),
        ("war_t1_su25_rockets_b", "attack_target", "surface", False, "rockets", True, "t2_base_04"),
        ("war_t1_ka52_attack_b", "attack_target", "surface", False, "all", True, "t2_strongpoint_07"),
        ("war_t2_a10_rockets_b", "attack_target", "surface", False, "rockets", True, "t1_base_04"),
        ("war_t2_fa18e_strike", "attack_target", "surface", False, "rockets", True, "t1_strongpoint_02"),
    ]
    trigger_insert = text.index("  debug_in_multiplayer{")
    triggers = warzone_trigger("warzone_initial_package", initial_units, None)
    triggers += "\n" + warzone_trigger("warzone_second_package", second_units, 55.0) + "\n"
    triggers += "\n" + warzone_trigger("warzone_third_package", third_units, 110.0) + "\n"
    initial_strikers = ("war_t1_su25_rockets_a", "war_t1_ka52_attack_a", "war_t2_a10_rockets_a")
    third_strikers = ("war_t1_su25_rockets_b", "war_t1_ka52_attack_b", "war_t2_a10_rockets_b", "war_t2_fa18e_strike")
    second_strikers = ("war_t1_su34_strike", "war_t2_f15e_strike")
    triggers += ai_targeting_window_trigger("warzone_initial_spaa_window_open", initial_strikers, 30.0, True) + "\n"
    triggers += ai_targeting_window_trigger("warzone_initial_spaa_window_close", initial_strikers, 36.0, False) + "\n"
    triggers += ai_targeting_window_trigger("warzone_second_spaa_window_open", second_strikers, 85.0, True) + "\n"
    triggers += ai_targeting_window_trigger("warzone_second_spaa_window_close", second_strikers, 91.0, False) + "\n"
    triggers += ai_targeting_window_trigger("warzone_third_spaa_window_open", third_strikers, 140.0, True) + "\n"
    triggers += ai_targeting_window_trigger("warzone_third_spaa_window_close", third_strikers, 146.0, False) + "\n"
    text = text[:trigger_insert] + triggers + text[trigger_insert:]

    # Rank-based selectors only work in the multiplayer room. Their removal is
    # what makes the original 2018 formations appear in this local mission.
    text = re.sub(r"^\s*rankRange:ip2=.*\n", "", text, flags=re.MULTILINE)

    reference = REFERENCE.read_text()
    ref_start, ref_end = named_armada(reference, "t2_player01")
    player = reference[ref_start:ref_end].replace(
        "wt_rafale_m_kh38mt4", "wt_rafale_m_warzone_kh38mt6_scalp_ir2_ins1"
    )
    player = player.replace(
        "[15589.947, 1500.0, 43840.151]", "[15589.947, 650.0, 43840.151]"
    )
    start, end = named_armada(text, "t2_player01")
    text = text[:start] + player + text[end:]

    aircraft = [
        armada("war_t1_su30_hunters_a", "su_30sm2", "su_30sm2_default", 1, 2, (-18000, 5600, 33000), "attack_player_B", "ATTACK_AIR", speed=260),
        armada("war_t1_su30_hunters_b", "su_30sm2", "su_30sm2_default", 1, 2, (-33000, 4800, 8000), "attack_player_B", "ATTACK_AIR", speed=260),
        armada("war_t1_mig35_cap_a", "mig_35", "mig_35_default", 1, 2, (-36000, 6200, 41000), "fire_at_will_air", "ATTACK_AIR", speed=250),
        armada("war_t1_mig35_cap_b", "mig_35", "mig_35_default", 1, 2, (-41000, 4300, -3000), "fire_at_will_air", "ATTACK_AIR", speed=250),
        armada("war_t1_su25_rockets_a", "su_25sm3", "su_25sm3_b8m", 1, 2, (-24000, 260, 32000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=170),
        armada("war_t1_su25_rockets_b", "su_25sm3", "su_25sm3_b8m", 1, 2, (-22000, 230, 8000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=170),
        armada("war_t1_su34_strike", "su_34", "su_34_rocket_s13", 1, 2, (-32000, 520, 48000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=220),
        armada("war_t1_ka52_attack_a", "ka_52", "ka_52_rocket_vyhr_c_8_ko", 1, 2, (-13000, 170, 38000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=70),
        armada("war_t1_ka52_attack_b", "ka_52", "ka_52_rocket_vyhr_c_8_ko", 1, 2, (-17000, 150, 17000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=70),
        armada("war_t2_rafale_cap_a", "rafale_c_f3", "rafale_c_f3_default", 2, 2, (34000, 5900, 36000), "fire_at_will_air", "ATTACK_AIR", speed=260),
        armada("war_t2_rafale_cap_b", "rafale_c_f3", "rafale_c_f3_default", 2, 2, (43000, 4500, 8000), "fire_at_will_air", "ATTACK_AIR", speed=260),
        armada("war_t2_a10_rockets_a", "a_10c", "a_10c_lau_131_default", 2, 2, (12000, 250, 46000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=155),
        armada("war_t2_a10_rockets_b", "a_10c", "a_10c_lau_131_default", 2, 2, (9000, 230, 18000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=155),
        armada("war_t2_f15e_strike", "f_15e", "f_15e_agm_65g", 2, 2, (28000, 720, 52000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=230),
        armada("war_t2_fa18e_strike", "fa_18e_block_2", "fa_18e_block_2_apkws_m282", 2, 2, (32000, 670, 28000), "hold_fire", "ATTACK_GROUND", protected_from_ai=True, speed=220),
    ]
    ships_at = text.index("  ships{")
    text = text[:ships_at] + "\n".join(aircraft) + "\n" + text[ships_at:]
    return text


def main() -> None:
    OUTPUT.write_text(build())


if __name__ == "__main__":
    main()
