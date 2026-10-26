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
    route: tuple[tuple[str, float, float, float, float], ...] = (),
) -> str:
    x, y, z = position
    protection = "\n      targetableByAi:b=no" if protected_from_ai else ""
    speed_line = f"\n      speed:r={speed:.1f}" if speed else ""
    strike = protected_from_ai and bool(route)
    route_text = "\n".join(
        f'''      {waypoint_name}{{
        type:t="normal"
        tm:m=[[1.0, 0.0, 0.0] [0.0, 1.0, 0.0] [0.0, 0.0, 1.0] [{waypoint_x:.1f}, {waypoint_y:.1f}, {waypoint_z:.1f}]]
        props{{
          speed:r={waypoint_speed:.1f}
          moveType:t="MOVETO"
        }}
      }}'''
        for waypoint_name, waypoint_x, waypoint_y, waypoint_z, waypoint_speed in route
    )
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
      canLeaveRouteForAtack:b={'no' if strike else 'yes'}
      targetAir:b={'yes' if task == 'ATTACK_AIR' else 'no'}
      targetGnd:b={'yes' if protected_from_ai else 'no'}
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
{route_text}
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
        if not protected:
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


def strike_commit_trigger(
    name: str,
    mission_time: float,
    comment: str,
    strikes: tuple[tuple[str, str, str, float], ...],
) -> str:
    actions: list[str] = []
    for unit, target, weapon_type, target_distance in strikes:
        actions.append(f'''      unitSetProperties{{
        object:t="{unit}"
        canLeaveRouteForAtack:b=yes
      }}''')
        action = attack_action(
            unit,
            "attack_target",
            "surface",
            weapon_type=weapon_type,
            target=target,
        ).replace("targetDistMax:r=65000.0", f"targetDistMax:r={target_distance:.1f}")
        action = "\n".join(
            line for line in action.splitlines() if "fightInArea" not in line and "fightArea" not in line
        )
        actions.append(action)
    return f'''  {name}{{
    is_enabled:b=yes
    comments:t="{comment}"
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
        "    deathPenaltyMul:r=0.2\n    maxRespawns:i=-1\n    respawnTimeMultiplier:r=0.1\n    allowEmptyTeams:b=yes\n    isLimitedFuel:b=no\n    isLimitedAmmo:b=no\n    fuelAmount:r=0.03",
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
    triggers += "\n" + strike_commit_trigger(
        "warzone_initial_strike_commit",
        70.0,
        "Initial low-level packages commit only after completing most of their ingress route.",
        (
            ("war_t1_su25_rockets_a", "t2_base_02", "rockets", 18000.0),
            ("war_t1_ka52_attack_a", "t2_strongpoint_02", "all", 12000.0),
            ("war_t2_a10_rockets_a", "t1_base_03", "rockets", 18000.0),
        ),
    ) + "\n"
    triggers += "\n" + strike_commit_trigger(
        "warzone_second_strike_commit",
        125.0,
        "Second low-level packages commit after a separated northern ingress.",
        (
            ("war_t1_su34_strike", "t2_base_03", "rockets", 20000.0),
            ("war_t2_f15e_strike", "t1_base_02", "all", 20000.0),
        ),
    ) + "\n"
    triggers += "\n" + strike_commit_trigger(
        "warzone_third_strike_commit",
        180.0,
        "Southern packages commit after their low-level ingress rather than climbing from spawn.",
        (
            ("war_t1_su25_rockets_b", "t2_base_04", "rockets", 18000.0),
            ("war_t1_ka52_attack_b", "t2_strongpoint_07", "all", 12000.0),
            ("war_t2_a10_rockets_b", "t1_base_04", "rockets", 18000.0),
            ("war_t2_fa18e_strike", "t1_strongpoint_02", "rockets", 20000.0),
        ),
    ) + "\n"
    initial_strikers = ("war_t1_su25_rockets_a", "war_t1_ka52_attack_a", "war_t2_a10_rockets_a")
    third_strikers = ("war_t1_su25_rockets_b", "war_t1_ka52_attack_b", "war_t2_a10_rockets_b", "war_t2_fa18e_strike")
    second_strikers = ("war_t1_su34_strike", "war_t2_f15e_strike")
    triggers += ai_targeting_window_trigger("warzone_initial_spaa_window_open", initial_strikers, 68.0, True) + "\n"
    triggers += ai_targeting_window_trigger("warzone_initial_spaa_window_close", initial_strikers, 98.0, False) + "\n"
    triggers += ai_targeting_window_trigger("warzone_second_spaa_window_open", second_strikers, 123.0, True) + "\n"
    triggers += ai_targeting_window_trigger("warzone_second_spaa_window_close", second_strikers, 153.0, False) + "\n"
    triggers += ai_targeting_window_trigger("warzone_third_spaa_window_open", third_strikers, 178.0, True) + "\n"
    triggers += ai_targeting_window_trigger("warzone_third_spaa_window_close", third_strikers, 208.0, False) + "\n"
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
    player = player.replace("    fuel:r=15.0", "    fuel:r=3.0")
    start, end = named_armada(text, "t2_player01")
    text = text[:start] + player + text[end:]

    aircraft = [
        armada("war_t1_su30_hunters_a", "su_30sm2", "su_30sm2_default", 1, 2, (-18000, 5600, 33000), "attack_player_B", "ATTACK_AIR", speed=260),
        armada("war_t1_su30_hunters_b", "su_30sm2", "su_30sm2_default", 1, 2, (-33000, 4800, 8000), "attack_player_B", "ATTACK_AIR", speed=260),
        armada("war_t1_mig35_cap_a", "mig_35", "mig_35_default", 1, 2, (-36000, 6200, 41000), "fire_at_will_air", "ATTACK_AIR", speed=250),
        armada("war_t1_mig35_cap_b", "mig_35", "mig_35_default", 1, 2, (-41000, 4300, -3000), "fire_at_will_air", "ATTACK_AIR", speed=250),
        armada("war_t1_su25_rockets_a", "su_25sm3", "su_25sm3_b8m", 1, 2, (-16000, 350, 52000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=170, route=(("war_t1_su25a_ingress_01", -9000, 350, 52000, 610), ("war_t1_su25a_ingress_02", 1000, 300, 49500, 610), ("war_t1_su25a_attack_gate", 5000, 300, 48500, 610))),
        armada("war_t1_su25_rockets_b", "su_25sm3", "su_25sm3_b8m", 1, 2, (-13000, 300, 20000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=170, route=(("war_t1_su25b_ingress_01", -8000, 280, 18000, 610), ("war_t1_su25b_attack_gate", -3000, 260, 16000, 610))),
        armada("war_t1_su34_strike", "su_34", "su_34_rocket_s13", 1, 2, (-16000, 500, 52000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=220, route=(("war_t1_su34_ingress_01", -9000, 500, 48000, 790), ("war_t1_su34_attack_gate", -1000, 450, 43000, 790))),
        armada("war_t1_ka52_attack_a", "ka_52", "ka_52_rocket_vyhr_c_8_ko", 1, 2, (-8000, 180, 47000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=70, route=(("war_t1_ka52a_ingress_01", -5000, 180, 45000, 250), ("war_t1_ka52a_attack_gate", -2500, 160, 43000, 250))),
        armada("war_t1_ka52_attack_b", "ka_52", "ka_52_rocket_vyhr_c_8_ko", 1, 2, (-10000, 160, 22000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=70, route=(("war_t1_ka52b_ingress_01", -8000, 160, 20000, 250), ("war_t1_ka52b_attack_gate", -6000, 150, 18500, 250))),
        armada("war_t2_rafale_cap_a", "rafale_c_f3", "rafale_c_f3_default", 2, 2, (34000, 5900, 36000), "fire_at_will_air", "ATTACK_AIR", speed=260),
        armada("war_t2_rafale_cap_b", "rafale_c_f3", "rafale_c_f3_default", 2, 2, (43000, 4500, 8000), "fire_at_will_air", "ATTACK_AIR", speed=260),
        armada("war_t2_a10_rockets_a", "a_10c", "a_10c_lau_131_default", 2, 2, (7000, 300, 48000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=155, route=(("war_t2_a10a_ingress_01", 0, 320, 42000, 555), ("war_t2_a10a_attack_gate", -7000, 300, 37000, 555))),
        armada("war_t2_a10_rockets_b", "a_10c", "a_10c_lau_131_default", 2, 2, (8000, 300, 20000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=155, route=(("war_t2_a10b_ingress_01", 2000, 300, 18000, 555), ("war_t2_a10b_attack_gate", -6000, 280, 15000, 555))),
        armada("war_t2_f15e_strike", "f_15e", "f_15e_agm_65g", 2, 2, (16000, 650, 52000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=230, route=(("war_t2_f15e_ingress_01", 9000, 600, 48000, 825), ("war_t2_f15e_attack_gate", 1000, 550, 44000, 825))),
        armada("war_t2_fa18e_strike", "fa_18e_block_2", "fa_18e_block_2_apkws_m282", 2, 2, (14000, 600, 30000), "hold_fire", "FLY_WAYPOINT", protected_from_ai=True, speed=220, route=(("war_t2_fa18e_ingress_01", 6000, 550, 34000, 825), ("war_t2_fa18e_attack_gate", 0, 500, 37000, 825))),
    ]
    ships_at = text.index("  ships{")
    text = text[:ships_at] + "\n".join(aircraft) + "\n" + text[ships_at:]
    return text


def main() -> None:
    OUTPUT.write_text(build())


if __name__ == "__main__":
    main()
