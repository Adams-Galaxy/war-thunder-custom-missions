#!/usr/bin/env python3
"""Build maintained Nuclear Escalation mission variants from source.blk."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MISSION_DIR = ROOT / "missions" / "ne-archipelago-2018"
SOURCE = MISSION_DIR / "source.blk"


def remove_object_groups_with_templates(text: str, templates: tuple[str, ...]) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0

    while index < len(lines):
        if lines[index] != "  objectGroups{\n":
            output.append(lines[index])
            index += 1
            continue

        block = [lines[index]]
        index += 1
        while index < len(lines):
            block.append(lines[index])
            index += 1
            if block[-1] == "  }\n":
                break

        block_text = "".join(block)
        if not any(f"{template}{{" in block_text for template in templates):
            output.extend(block)

    return "".join(output)


def remove_nested_blocks(text: str, block_name: str, indent: str = "      ") -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    opening = f"{indent}{block_name}{{\n"

    while index < len(lines):
        if lines[index] != opening:
            output.append(lines[index])
            index += 1
            continue

        depth = 0
        while index < len(lines):
            depth += lines[index].count("{") - lines[index].count("}")
            index += 1
            if depth == 0:
                break

    return "".join(output)


def tag_title(text: str, tag: str) -> str:
    return re.sub(
        r'^(\s*locName:t="[^"]*)"$',
        rf"\1 [{tag}]\"",
        text,
        count=1,
        flags=re.MULTILINE,
    )


S300_ZERO_AMMO_SETTINGS = '''      sam_site_s300{
        "sam_site__unitSettings:array"{
          "unit:object"{
            name:t="ussr_ai_sam_launcher_5p85se"
            templateName:t="tank+sam_site_unit"
            spawnName:t="launcher"
            death_substract_tickets:i=30
            count:i=4
            rearmTimeOnField:r=1000000000.0
            "bulletsCount:list<i>"{
              c:i=0
            }
          }
          "unit:object"{
            name:t="ussr_ai_sam_radar_5n63s"
            templateName:t="tank+sam_site_unit"
            spawnName:t="tracker_radar"
            death_substract_tickets:i=100
            count:i=1
          }
          "unit:object"{
            name:t="ussr_ai_sam_radar_5n64s"
            templateName:t="tank+sam_site_unit"
            spawnName:t="detector_radar"
            death_substract_tickets:i=100
            count:i=1
          }
        }
'''


SAMPT_ZERO_AMMO_SETTINGS = '''      sam_site_sampt{
        "sam_site__unitSettings:array"{
          "unit:object"{
            name:t="it_samp_t_launcher"
            templateName:t="tank+sam_site_unit"
            spawnName:t="launcher"
            death_substract_tickets:i=30
            count:i=4
            dontCreateChar:b=yes
            rearmTimeOnField:r=1000000000.0
            "bulletsCount:list<i>"{
              c:i=0
            }
          }
          "unit:object"{
            name:t="it_samp_t_fcs"
            templateName:t="tank+sam_site_unit"
            spawnName:t="tracker_radar"
            death_substract_tickets:i=100
            count:i=2
          }
        }
'''


def add_zero_ammo_sam_settings(text: str) -> str:
    s300_count = text.count("      sam_site_s300{\n")
    sampt_count = text.count("      sam_site_sampt{\n")
    if (s300_count, sampt_count) != (8, 8):
        raise ValueError(
            f"Expected 8 S-300 and 8 SAMP/T sites, got {s300_count} and {sampt_count}"
        )
    text = text.replace("      sam_site_s300{\n", S300_ZERO_AMMO_SETTINGS)
    return text.replace("      sam_site_sampt{\n", SAMPT_ZERO_AMMO_SETTINGS)


def assert_balanced(text: str) -> None:
    if text.count("{") != text.count("}"):
        raise ValueError("Generated BLK has unbalanced braces")


def write_variant(name: str, text: str) -> None:
    assert_balanced(text)
    (MISSION_DIR / name).write_text(text, encoding="utf-8")


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")

    no_lrsam = remove_object_groups_with_templates(
        source,
        ("sam_site_s300", "sam_site_sampt"),
    )
    if no_lrsam.count("sam_site_s300{") or no_lrsam.count("sam_site_sampt{"):
        raise ValueError("Long-range SAM templates remain in no-lrsam variant")
    write_variant("no-lrsam.blk", tag_title(no_lrsam, "NO LRSAM"))

    no_lrsam_no_airfield_aa = remove_nested_blocks(no_lrsam, "airfield_aa_2018")
    if no_lrsam_no_airfield_aa.count("airfield_aa_2018{"):
        raise ValueError("Airfield AA templates remain in no-airfield-AA variant")
    write_variant(
        "no-lrsam-no-airfield-aa.blk",
        tag_title(no_lrsam_no_airfield_aa, "NO LRSAM / NO AIRFIELD AA"),
    )

    silent_lrsam = add_zero_ammo_sam_settings(source)
    if silent_lrsam.count("rearmTimeOnField:r=1000000000.0") != 16:
        raise ValueError("Not every strategic SAM launcher definition was overridden")
    write_variant(
        "silent-lrsam-experimental.blk",
        tag_title(silent_lrsam, "SILENT LRSAM EXPERIMENT"),
    )


if __name__ == "__main__":
    main()
