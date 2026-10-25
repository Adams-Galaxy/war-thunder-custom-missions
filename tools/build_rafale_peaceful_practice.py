#!/usr/bin/env python3
"""Build the peaceful South-Eastern City Rafale practice mission."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "missions/ne-southeastern-city/peaceful-exploration.blk"
REFERENCE = (
    ROOT
    / "experiments/rafale-m-f3r-loadouts/UserMissions"
    / "usr_wt_rafale_kh38mt4.mission.blk"
)
OUTPUT = (
    ROOT
    / "experiments/rafale-m-f3r-loadouts/UserMissions"
    / "usr_wt_rafale_peaceful_practice_kh38mt6_scalp3.mission.blk"
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
    needle = f'name:t="{name}"'
    name_at = text.index(needle)
    start = text.rfind("  armada{", 0, name_at)
    if start < 0:
        raise ValueError(f"armada {name!r} not found")
    return start, block_end(text, start)


def replace_named_block(text: str, block_name: str, replacement: str) -> str:
    start = text.index(f"  {block_name}{{")
    end = block_end(text, start)
    return text[:start] + replacement + text[end:]


def build() -> str:
    text = SOURCE.read_text()

    # A User Mission has one selected player aircraft. The underlying peaceful
    # battle entities, objectives, ticket logic, and victory triggers remain.
    player_start = text.index("  player{")
    mission_start = text.index("  mission{", player_start)
    text = (
        text[:player_start]
        + '  player{\n    army:i=2\n    wing:t="t2_player01"\n  }\n'
        + text[mission_start:]
    )
    text = text.replace('    type:t="domination"', '    name:t="wt_rafale_peaceful_practice_kh38mt6_scalp3"\n    type:t="singleMission"', 1)
    text = text.replace("    afterRespawnDelaySec:i=30", "    afterRespawnDelaySec:i=1", 1)
    text = text.replace(
        '    locName:t="Nuclear Escalation · Southeastern City [PEACEFUL EXPLORATION]"',
        '    locName:t="Southeastern City · Peaceful Rafale Practice"',
        1,
    )
    text = text.replace(
        '    locDesc:t="Custom version of the official Nuclear Escalation mission. Stars mark Soviet-aligned air defenses; crosses mark NATO. All map units remain present, strategic sites have zero engagement channels, and every player vehicle is continuously hidden from AI targeting and made immortal. Quick-start aircraft, helicopter, and naval spawns are enabled."',
        '    locDesc:t="Peaceful Exploration with all map units physically present. Fly an invisible and invincible Rafale carrying 6 powered fire-and-forget Kh-38MTs and 3 native-navigation SCALP-EG proxies. Player respawns are unlimited; fuel and ammunition are unlimited; airborne weapon rearm is accelerated."',
        1,
    )
    text = text.replace(
        "    deathPenaltyMul:r=0.2",
        "    deathPenaltyMul:r=0.2\n    maxRespawns:i=-1\n    respawnTimeMultiplier:r=0.1\n    allowEmptyTeams:b=yes\n    isLimitedFuel:b=no\n    isLimitedAmmo:b=no",
        1,
    )

    practice_trigger = '''  practice_player_support{
    is_enabled:b=yes
    comments:t="Reapply peaceful protection and fast Arcade airborne rearm after spawn or death."
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
      unitSetProperties{
        object:t="t2_player01"
        targetableByAi:b=no
        isImmortal:b=yes
        speed:r=900.0
      }
      unitForceRearmSpeed{
        target:t="t2_player01"
        rearmSpeedK:r=80.0
      }
    }
    else_actions{

    }
  }'''
    text = replace_named_block(text, "debug_in_single", practice_trigger)
    text = text.replace("  debug_in_multiplayer{\n    is_enabled:b=yes", "  debug_in_multiplayer{\n    is_enabled:b=no", 1)

    # Multiplayer balance-rank filters do not resolve in a local singleMission;
    # removing only those selectors keeps the intended 2018 formations present.
    text = re.sub(r"^\s*rankRange:ip2=.*\n", "", text, flags=re.MULTILINE)

    reference = REFERENCE.read_text()
    ref_start, ref_end = named_armada(reference, "t2_player01")
    player = reference[ref_start:ref_end]
    player = player.replace("wt_rafale_m_kh38mt4", "wt_rafale_m_practice_kh38mt6_scalp3")
    start, end = named_armada(text, "t2_player01")
    text = text[:start] + player + text[end:]
    return text


def main() -> None:
    OUTPUT.write_text(build())


if __name__ == "__main__":
    main()
