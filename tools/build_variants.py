#!/usr/bin/env python3
"""Build maintained Nuclear Escalation mission variants from source.blk."""

from pathlib import Path
import math
import re


ROOT = Path(__file__).resolve().parents[1]
MISSION_DIR = ROOT / "missions" / "ne-archipelago-2018"
SOURCE = MISSION_DIR / "source.blk"
SOUTHEASTERN_CITY_DIR = ROOT / "missions" / "ne-southeastern-city"
SOUTHEASTERN_CITY_SOURCE = SOUTHEASTERN_CITY_DIR / "source.blk"
ARCHIPELAGO_SOURCE = MISSION_DIR / "source.blk"
SOUTHEASTERN_DIAGNOSTICS_DIR = SOUTHEASTERN_CITY_DIR / "diagnostics"


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


def set_english_metadata(text: str, tag: str, detail: str) -> str:
    title = f'Nuclear Escalation · Archipelago · Training (2018) [{tag}]'
    description = (
        "Custom version of the event mission with 2018-era air defenses. "
        "Stars mark Soviet-aligned air defenses; crosses mark NATO. "
        f"{detail}"
    )
    text, title_count = re.subn(
        r'^\s*locName:t="[^"]*"$',
        f'    locName:t="{title}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    text, description_count = re.subn(
        r'^\s*locDesc:t="[^"]*"$',
        f'    locDesc:t="{description}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if (title_count, description_count) != (1, 1):
        raise ValueError("Could not replace mission title and description")
    return text


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


def disable_sam_channels(text: str) -> str:
    """Set the server-side strategic-site channel limits to zero.

    Unlike the unit-settings array experiment, these are ordinary scalar ECS
    components already supported in each mission object's template overlay.
    """
    site_pattern = re.compile(r"(      sam_site_(?:s300|sampt)\{\n)")
    matches = site_pattern.findall(text)
    if len(matches) != 16:
        raise ValueError(f"Expected 16 strategic SAM sites, got {len(matches)}")
    return site_pattern.sub(
        r"\1"
        "        sam_site__missile_channels_max:i=0\n"
        "        sam_site__target_channels_max:i=0\n",
        text,
    )


def team1_airfield_roster(
    hq11_threat_radius: float, hq11_ammo: int = 8, hq11_radar_managed: bool = True
) -> str:
    hq11_template = (
        "tank+nuclear_escalation_spaa_radar_on"
        if hq11_radar_managed
        else "tank+nuclear_escalation_spaa_radar_off"
    )
    return f'''        "units_spawn_on_init__unitSettings:array"{{
          "unit:object"{{
            name:t="ussr_pantsyr_s1"
            templateName:t="tank+nuclear_escalation_spaa_radar_on"
            death_substract_tickets:i=20
            count:i=1
            threatSearchRad:r=23000.0
            dontCreateChar:b=yes
            "mods:list<t>"{{
              m:t="tank_tool_kit"
              m:t="manual_extinguisher"
            }}
            "bulletNames:list<t>"{{
              name:t="30mm_2a38_HE"
              name:t=""
            }}
            "bulletsCount:list<i>"{{
              c:i=0
              c:i=12
            }}
          }}
          "unit:object"{{
            name:t="ussr_zprk_2s6"
            templateName:t="tank+nuclear_escalation_spaa_radar_on"
            death_substract_tickets:i=20
            count:i=2
            threatSearchRad:r=12000.0
            dontCreateChar:b=yes
            "mods:list<t>"{{
              m:t="tank_tool_kit"
              m:t="manual_extinguisher"
              m:t="2s6_upgrade_modification"
            }}
            "bulletNames:list<t>"{{
              name:t="30mm_2a38_HE"
              name:t=""
            }}
            "bulletsCount:list<i>"{{
              c:i=0
              c:i=8
            }}
          }}
          "unit:object"{{
            name:t="ussr_2s38"
            templateName:t="tank+nuclear_escalation_spaa_radar_off"
            death_substract_tickets:i=20
            count:i=2
            dontCreateChar:b=yes
            "mods:list<t>"{{
              m:t="tank_tool_kit"
              m:t="manual_extinguisher"
            }}
            "bulletNames:list<t>"{{
              name:t="57mm_HE_VT"
            }}
          }}
          "unit:object"{{
            name:t="cn_hq_11"
            templateName:t="{hq11_template}"
            death_substract_tickets:i=30
            threatSearchRad:r={hq11_threat_radius:.1f}
            "mods:list<t>"{{
              m:t="tank_tool_kit"
              m:t="manual_extinguisher"
            }}
            "bulletNames:list<t>"{{
            }}
            "bulletsCount:list<i>"{{
              c:i={hq11_ammo}
            }}
          }}
        }}
'''


def render_unit_settings_array(
    component: str, units: list[dict[str, object]], indent: str = "        "
) -> str:
    """Render the subset of unit-setting fields used by Nuclear Escalation."""
    scalar_fields = (
        ("name", "t"),
        ("templateName", "t"),
        ("death_substract_tickets", "i"),
        ("spawnName", "t"),
        ("count", "i"),
        ("threatSearchRad", "r"),
        ("dontCreateChar", "b"),
    )
    lines = [f'{indent}"{component}"{{\n']
    unit_indent = indent + "  "
    field_indent = unit_indent + "  "
    list_indent = field_indent + "  "
    for unit in units:
        lines.append(f'{unit_indent}"unit:object"{{\n')
        for field, kind in scalar_fields:
            if field not in unit:
                continue
            value = unit[field]
            if kind == "t":
                rendered = f'"{value}"'
            elif kind == "b":
                rendered = "yes" if value else "no"
            elif kind == "r":
                rendered = f"{float(value):.1f}"
            else:
                rendered = str(value)
            lines.append(f"{field_indent}{field}:{kind}={rendered}\n")
        for component_name, item_name, kind, field in (
            ("mods:list<t>", "m", "t", "mods"),
            ("bulletNames:list<t>", "name", "t", "bullet_names"),
            ("bulletsCount:list<i>", "c", "i", "bullet_counts"),
        ):
            if field not in unit:
                continue
            values = unit[field]
            if not isinstance(values, list):
                values = [values]
            lines.append(f'{field_indent}"{component_name}"{{\n')
            for value in values:
                rendered = f'"{value}"' if kind == "t" else str(value)
                lines.append(f"{list_indent}{item_name}:{kind}={rendered}\n")
            lines.append(f"{field_indent}}}\n")
        lines.append(f"{unit_indent}}}\n")
    lines.append(f"{indent}}}\n")
    return "".join(lines)


def short_range_airfield_roster(
    army: int,
    tunguska_radius: float,
    crotale_radius: float,
    pantsir_radius: float,
    long_airfield_radius: float,
) -> list[dict[str, object]]:
    if army == 1:
        return [
            {
                "name": "ussr_pantsyr_s1",
                "templateName": "tank+nuclear_escalation_spaa_radar_on",
                "death_substract_tickets": 20,
                "count": 1,
                "threatSearchRad": pantsir_radius,
                "dontCreateChar": True,
                "mods": ["tank_tool_kit", "manual_extinguisher"],
                "bullet_names": ["30mm_2a38_HE", ""],
                "bullet_counts": [0, 12],
            },
            {
                "name": "ussr_zprk_2s6",
                "templateName": "tank+nuclear_escalation_spaa_radar_on",
                "death_substract_tickets": 20,
                "count": 2,
                "threatSearchRad": tunguska_radius,
                "dontCreateChar": True,
                "mods": [
                    "tank_tool_kit",
                    "manual_extinguisher",
                    "2s6_upgrade_modification",
                ],
                "bullet_names": ["30mm_2a38_HE", ""],
                "bullet_counts": [0, 8],
            },
            {
                "name": "ussr_2s38",
                "templateName": "tank+nuclear_escalation_spaa_radar_off",
                "death_substract_tickets": 20,
                "count": 2,
                "dontCreateChar": True,
                "mods": ["tank_tool_kit", "manual_extinguisher"],
                "bullet_names": ["57mm_HE_VT"],
            },
            {
                "name": "cn_hq_11",
                "templateName": "tank+nuclear_escalation_spaa_radar_on",
                "death_substract_tickets": 30,
                "threatSearchRad": long_airfield_radius,
                "mods": ["tank_tool_kit", "manual_extinguisher"],
                "bullet_names": [],
                "bullet_counts": [8],
            },
        ]
    return [
        {
            "name": "sw_crotale_ng",
            "templateName": "tank+nuclear_escalation_spaa_radar_on",
            "death_substract_tickets": 20,
            "count": 3,
            "threatSearchRad": crotale_radius,
            "dontCreateChar": True,
            "mods": ["tank_tool_kit", "manual_extinguisher"],
            "bullet_counts": [8],
        },
        {
            "name": "it_otomatic",
            "templateName": "tank+nuclear_escalation_spaa_radar_off",
            "death_substract_tickets": 20,
            "count": 2,
            "dontCreateChar": True,
            "mods": ["tank_tool_kit", "manual_extinguisher"],
            "bullet_names": ["76mm_oto_HE_VT"],
            "bullet_counts": [],
        },
        {
            "name": "il_spyder_aio",
            "templateName": "tank+nuclear_escalation_spaa_radar_on",
            "death_substract_tickets": 30,
            "threatSearchRad": long_airfield_radius,
            "dontCreateChar": True,
            "mods": ["tank_tool_kit", "manual_extinguisher"],
            "bullet_names": ["160mm_derby_er_aam"],
            "bullet_counts": [8],
        },
    ]


def short_range_medium_spaa(
    army: int,
    radius: float,
    *,
    count: int = 1,
    spawn_name: str | None = None,
    airfield_template: bool = False,
) -> dict[str, object]:
    unit: dict[str, object]
    if army == 1:
        unit = {
            "name": "ussr_zprk_2s6",
            "templateName": (
                "tank+nuclear_escalation_spaa_radar_on"
                if airfield_template
                else "tank+nuclear_escalation_spaa_with_threat_radar"
            ),
            "death_substract_tickets": 20,
            "count": count,
            "threatSearchRad": radius,
            "dontCreateChar": True,
            "mods": [
                "tank_tool_kit",
                "manual_extinguisher",
                "2s6_upgrade_modification",
            ],
            "bullet_names": ["30mm_2a38_HE", ""],
            "bullet_counts": [0, 8],
        }
    else:
        unit = {
            "name": "sw_crotale_ng",
            "templateName": (
                "tank+nuclear_escalation_spaa_radar_on"
                if airfield_template
                else "tank+nuclear_escalation_spaa_with_threat_radar"
            ),
            "death_substract_tickets": 20,
            "count": count,
            "threatSearchRad": radius,
            "dontCreateChar": True,
            "mods": ["tank_tool_kit", "manual_extinguisher"],
            "bullet_names": [],
            "bullet_counts": [8],
        }
    if spawn_name is not None:
        unit["spawnName"] = spawn_name
    return unit


def short_range_strongpoint_roster(
    army: int, tunguska_radius: float, crotale_radius: float
) -> list[dict[str, object]]:
    if army == 1:
        ground_units = [
            {
                "name": "ussr_t_80bvm",
                "templateName": "tank+nuclear_escalation_tank",
                "count": 3,
                "dontCreateChar": True,
                "mods": ["tank_tool_kit", "manual_extinguisher"],
                "bullet_names": ["USSR_APDS_FS"],
            },
            {
                "name": "ussr_bmp_3",
                "templateName": "tank+nuclear_escalation_tank",
                "count": 2,
                "dontCreateChar": True,
                "mods": ["tank_tool_kit", "manual_extinguisher"],
                "bullet_names": ["30mm_2a72_AP"],
            },
        ]
    else:
        ground_units = [
            {
                "name": "us_m1a2_sep2_abrams",
                "templateName": "tank+nuclear_escalation_tank",
                "count": 3,
                "dontCreateChar": True,
                "mods": ["tank_tool_kit", "manual_extinguisher"],
                "bullet_names": ["NATO_APDS_FS"],
            },
            {
                "name": "us_m3a3_bradley",
                "templateName": "tank+nuclear_escalation_tank",
                "count": 2,
                "dontCreateChar": True,
                "mods": ["tank_tool_kit", "manual_extinguisher"],
            },
        ]
    radius = tunguska_radius if army == 1 else crotale_radius
    return ground_units + [short_range_medium_spaa(army, radius)]


def short_range_factory_column(
    army: int, factory_kind: str, tunguska_radius: float, crotale_radius: float
) -> list[dict[str, object]]:
    radius = tunguska_radius if army == 1 else crotale_radius
    spaa = short_range_medium_spaa(army, radius)
    if army == 1:
        suffix = "fuel" if factory_kind == "fuel" else "awning_ammo"
        carrier = f"wheeled_vehicles/ussr_kamaz_4310_{suffix}_carrier"
    else:
        suffix = "fuel" if factory_kind == "fuel" else "awning_ammo"
        model = "m978" if factory_kind == "fuel" else "m939"
        carrier = f"wheeled_vehicles/us_{model}_{suffix}_carrier"
    return [
        spaa,
        {
            "name": carrier,
            "templateName": "simple_tank+nuclear_escalation_tank",
            "count": 4,
        },
    ]


def override_all_direct_2018_air_defenses(
    text: str,
    *,
    tunguska_radius: float = 6000.0,
    crotale_radius: float = 6000.0,
    pantsir_radius: float = 8000.0,
    long_airfield_radius: float = 18000.0,
) -> str:
    """Override every directly configurable 2018 defense source.

    Assembly areas create later tank-factory entities from a protected template;
    their future moving columns cannot inherit mission-local array overrides.
    """
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    modified = {"airfield": 0, "strongpoint": 0, "cover": 0, "storage": 0}

    while index < len(lines):
        if lines[index] != "  objectGroups{\n":
            output.append(lines[index])
            index += 1
            continue
        block_lines = [lines[index]]
        index += 1
        depth = 1
        while index < len(lines) and depth:
            line = lines[index]
            block_lines.append(line)
            depth += line.count("{") - line.count("}")
            index += 1
        block = "".join(block_lines)
        army_match = re.search(r"(?m)^      army:i=([12])$", block)
        if not army_match:
            output.append(block)
            continue
        army = int(army_match.group(1))

        if "      airfield_aa_2018{\n" in block:
            roster = short_range_airfield_roster(
                army,
                tunguska_radius,
                crotale_radius,
                pantsir_radius,
                long_airfield_radius,
            )
            payload = render_unit_settings_array(
                "units_spawn_on_init__unitSettings:array", roster
            )
            block = block.replace(
                "      airfield_aa_2018{\n",
                "      airfield_aa_2018{\n" + payload,
                1,
            )
            modified["airfield"] += 1
        elif "      strongpoint_2018{\n" in block:
            roster = short_range_strongpoint_roster(
                army, tunguska_radius, crotale_radius
            )
            payload = render_unit_settings_array(
                "units_spawn_on_init__unitSettings:array", roster
            )
            block = block.replace(
                "      strongpoint_2018{\n",
                "      strongpoint_2018{\n" + payload,
                1,
            )
            modified["strongpoint"] += 1
        elif re.search(r"      aa_cover_(?:ussr_zprk_2s6|sw_crotale_ng)\{\n", block):
            radius = tunguska_radius if army == 1 else crotale_radius
            roster = [short_range_medium_spaa(army, radius, airfield_template=True)]
            payload = render_unit_settings_array(
                "units_spawn_on_init__unitSettings:array", roster
            )
            block = re.sub(
                r"(      aa_cover_(?:ussr_zprk_2s6|sw_crotale_ng)\{\n)",
                lambda match: match.group(1) + payload,
                block,
                count=1,
            )
            modified["cover"] += 1
        else:
            storage_match = re.search(
                r'      "fortification\+(fuel|ammo)_factory_2018"\{\n', block
            )
            if storage_match:
                kind = storage_match.group(1)
                radius = tunguska_radius if army == 1 else crotale_radius
                static_roster = [
                    short_range_medium_spaa(
                        army,
                        radius,
                        count=3,
                        spawn_name="spaa",
                        airfield_template=True,
                    )
                ]
                payload = render_unit_settings_array(
                    "units_spawn_on_init__unitSettings:array", static_roster
                )
                payload += render_unit_settings_array(
                    f"equip_factory__columnUnitsSettings{army}:array",
                    short_range_factory_column(
                        army, kind, tunguska_radius, crotale_radius
                    ),
                )
                marker = storage_match.group(0)
                block = block.replace(marker, marker + payload, 1)
                modified["storage"] += 1
        output.append(block)

    expected = {"airfield": 12, "strongpoint": 16, "cover": 32, "storage": 12}
    if modified != expected:
        raise ValueError(f"Unexpected short-range override counts: {modified}")
    return "".join(output)


def override_team1_airfield_roster(
    text: str,
    hq11_threat_radius: float,
    hq11_ammo: int = 8,
    hq11_radar_managed: bool = True,
) -> str:
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    modified = 0
    insertion = team1_airfield_roster(
        hq11_threat_radius, hq11_ammo, hq11_radar_managed
    )

    while index < len(lines):
        if lines[index] != "  objectGroups{\n":
            output.append(lines[index])
            index += 1
            continue

        block = [lines[index]]
        index += 1
        depth = 1
        while index < len(lines) and depth:
            line = lines[index]
            block.append(line)
            depth += line.count("{") - line.count("}")
            index += 1

        block_text = "".join(block)
        if "      airfield_aa_2018{\n" in block_text and "      army:i=1\n" in block_text:
            block_text = block_text.replace(
                "      airfield_aa_2018{\n",
                "      airfield_aa_2018{\n" + insertion,
                1,
            )
            modified += 1
        output.append(block_text)

    if modified != 6:
        raise ValueError(f"Expected 6 team-1 airfields, modified {modified}")
    return "".join(output)


def assert_balanced(text: str) -> None:
    if text.count("{") != text.count("}"):
        raise ValueError("Generated BLK has unbalanced braces")


def pretty_object_group_spans(text: str) -> list[tuple[int, int]]:
    """Return spans for objectGroups blocks in wt_ext_cli's BlkText format."""
    spans: list[tuple[int, int]] = []
    offset = 0
    start: int | None = None
    depth = 0
    for line in text.splitlines(keepends=True):
        if start is None and line == "\tobjectGroups {\n":
            start = offset
            depth = 0
        if start is not None:
            depth += line.count("{") - line.count("}")
            if depth == 0:
                spans.append((start, offset + len(line)))
                start = None
        offset += len(line)
    if start is not None:
        raise ValueError("Unterminated objectGroups block")
    return spans


def remove_pretty_object_groups_with_templates(
    text: str, templates: tuple[str, ...]
) -> str:
    spans = pretty_object_group_spans(text)
    output: list[str] = []
    cursor = 0
    removed = 0
    for start, end in spans:
        block = text[start:end]
        output.append(text[cursor:start])
        if any(re.search(rf"^\s*{re.escape(template)}\s*\{{", block, re.MULTILINE)
               for template in templates):
            removed += 1
        else:
            output.append(block)
        cursor = end
    output.append(text[cursor:])
    if removed != 16:
        raise ValueError(f"Expected to remove 16 strategic sites, removed {removed}")
    return "".join(output)


def disable_pretty_sam_channels(text: str) -> str:
    pattern = re.compile(r"(?m)^(\s*)(sam_site_(?:s300|sampt)\s*\{\n)")
    matches = pattern.findall(text)
    if len(matches) != 16:
        raise ValueError(f"Expected 16 strategic SAM sites, got {len(matches)}")
    return pattern.sub(
        lambda match: (
            match.group(1)
            + match.group(2)
            + match.group(1)
            + "\tsam_site__missile_channels_max:i=0\n"
            + match.group(1)
            + "\tsam_site__target_channels_max:i=0\n"
        ),
        text,
    )


def set_pretty_english_metadata(text: str, tag: str, detail: str) -> str:
    title = f"Nuclear Escalation · Southeastern City [{tag}]"
    description = (
        "Custom version of the official Nuclear Escalation mission. "
        "Stars mark Soviet-aligned air defenses; crosses mark NATO. "
        f"{detail}"
    )
    text, title_count = re.subn(
        r'(?m)^(\s*)locName:t\s*=\s*"[^"]*"$',
        rf'\1locName:t="{title}"',
        text,
        count=1,
    )
    text, description_count = re.subn(
        r'(?m)^(\s*)locDesc:t\s*=\s*"[^"]*"$',
        rf'\1locDesc:t="{description}"',
        text,
        count=1,
    )
    if (title_count, description_count) != (1, 1):
        raise ValueError("Could not replace Southeastern City metadata")
    return text


def pretty_team1_airfield_roster(hq11_threat_radius: float) -> str:
    return f'''\t\t\t\t"units_spawn_on_init__unitSettings:array" {{
\t\t\t\t\t"unit:object" {{
\t\t\t\t\t\tname:t = "ussr_pantsyr_s1"
\t\t\t\t\t\ttemplateName:t = "tank+nuclear_escalation_spaa_radar_on"
\t\t\t\t\t\tdeath_substract_tickets:i = 20
\t\t\t\t\t\tcount:i = 1
\t\t\t\t\t\tthreatSearchRad:r = 23000.0
\t\t\t\t\t\tdontCreateChar:b = true
\t\t\t\t\t\t"mods:list<t>" {{
\t\t\t\t\t\t\tm:t = "tank_tool_kit"
\t\t\t\t\t\t\tm:t = "manual_extinguisher"
\t\t\t\t\t\t}}
\t\t\t\t\t\t"bulletNames:list<t>" {{
\t\t\t\t\t\t\tname:t = "30mm_2a38_HE"
\t\t\t\t\t\t\tname:t = ""
\t\t\t\t\t\t}}
\t\t\t\t\t\t"bulletsCount:list<i>" {{
\t\t\t\t\t\t\tc:i = 0
\t\t\t\t\t\t\tc:i = 12
\t\t\t\t\t\t}}
\t\t\t\t\t}}
\t\t\t\t\t"unit:object" {{
\t\t\t\t\t\tname:t = "ussr_zprk_2s6"
\t\t\t\t\t\ttemplateName:t = "tank+nuclear_escalation_spaa_radar_on"
\t\t\t\t\t\tdeath_substract_tickets:i = 20
\t\t\t\t\t\tcount:i = 2
\t\t\t\t\t\tthreatSearchRad:r = 12000.0
\t\t\t\t\t\tdontCreateChar:b = true
\t\t\t\t\t\t"mods:list<t>" {{
\t\t\t\t\t\t\tm:t = "tank_tool_kit"
\t\t\t\t\t\t\tm:t = "manual_extinguisher"
\t\t\t\t\t\t\tm:t = "2s6_upgrade_modification"
\t\t\t\t\t\t}}
\t\t\t\t\t\t"bulletNames:list<t>" {{
\t\t\t\t\t\t\tname:t = "30mm_2a38_HE"
\t\t\t\t\t\t\tname:t = ""
\t\t\t\t\t\t}}
\t\t\t\t\t\t"bulletsCount:list<i>" {{
\t\t\t\t\t\t\tc:i = 0
\t\t\t\t\t\t\tc:i = 8
\t\t\t\t\t\t}}
\t\t\t\t\t}}
\t\t\t\t\t"unit:object" {{
\t\t\t\t\t\tname:t = "ussr_2s38"
\t\t\t\t\t\ttemplateName:t = "tank+nuclear_escalation_spaa_radar_off"
\t\t\t\t\t\tdeath_substract_tickets:i = 20
\t\t\t\t\t\tcount:i = 2
\t\t\t\t\t\tdontCreateChar:b = true
\t\t\t\t\t\t"mods:list<t>" {{
\t\t\t\t\t\t\tm:t = "tank_tool_kit"
\t\t\t\t\t\t\tm:t = "manual_extinguisher"
\t\t\t\t\t\t}}
\t\t\t\t\t\t"bulletNames:list<t>" {{
\t\t\t\t\t\t\tname:t = "57mm_HE_VT"
\t\t\t\t\t\t}}
\t\t\t\t\t}}
\t\t\t\t\t"unit:object" {{
\t\t\t\t\t\tname:t = "cn_hq_11"
\t\t\t\t\t\ttemplateName:t = "tank+nuclear_escalation_spaa_radar_on"
\t\t\t\t\t\tdeath_substract_tickets:i = 30
\t\t\t\t\t\tthreatSearchRad:r = {hq11_threat_radius:.1f}
\t\t\t\t\t\t"mods:list<t>" {{
\t\t\t\t\t\t\tm:t = "tank_tool_kit"
\t\t\t\t\t\t\tm:t = "manual_extinguisher"
\t\t\t\t\t\t}}
\t\t\t\t\t\t"bulletNames:list<t>" {{
\t\t\t\t\t\t}}
\t\t\t\t\t\t"bulletsCount:list<i>" {{
\t\t\t\t\t\t\tc:i = 8
\t\t\t\t\t\t}}
\t\t\t\t\t}}
\t\t\t\t}}
'''


def override_pretty_team1_airfields(text: str, hq11_threat_radius: float) -> str:
    output: list[str] = []
    cursor = 0
    modified = 0
    insertion = pretty_team1_airfield_roster(hq11_threat_radius)
    for start, end in pretty_object_group_spans(text):
        block = text[start:end]
        output.append(text[cursor:start])
        if ("\t\t\tairfield_aa_2018 {\n" in block
                and re.search(r"^\s*army:i\s*=\s*1$", block, re.MULTILINE)):
            block = block.replace(
                "\t\t\tairfield_aa_2018 {\n",
                "\t\t\tairfield_aa_2018 {\n" + insertion,
                1,
            )
            modified += 1
        output.append(block)
        cursor = end
    output.append(text[cursor:])
    if modified != 5:
        raise ValueError(f"Expected 5 team-1 airfields, modified {modified}")
    return "".join(output)


def compact_scalar_syntax(text: str) -> str:
    """Use the canonical scalar syntax accepted by the game's URL loader."""
    text = re.sub(r"(:[A-Za-z0-9<>]+)\s*=\s*", r"\1=", text)
    text = re.sub(r"(:b=)true\b", r"\1yes", text)
    text = re.sub(r"(:b=)false\b", r"\1no", text)
    text = re.sub(r"(?m)^(\s*)(.*?)\s+\{$", r"\1\2{", text)
    return text.expandtabs(2)


def quote_plus_sign_storage_templates(text: str) -> str:
    """Quote storage template keys required by the remote mission parser."""
    text, count = re.subn(
        r'(?m)^(\s*)(fortification\+(?:fuel|ammo)_factory_2018)\s*\{$',
        r'\1"\2"{',
        text,
    )
    if count != 8:
        raise ValueError(f"Expected to quote 8 storage templates, got {count}")
    return text


def top_level_block_span(text: str, name: str) -> tuple[int, int, int]:
    """Return block start, inner start, and block end for one top-level block."""
    match = re.search(rf"(?m)^{re.escape(name)}\s*\{{\n", text)
    if not match:
        raise ValueError(f"Could not find top-level {name} block")
    depth = 1
    cursor = match.end()
    for line in text[cursor:].splitlines(keepends=True):
        depth += line.count("{") - line.count("}")
        cursor += len(line)
        if depth == 0:
            return match.start(), match.end(), cursor
    raise ValueError(f"Unterminated top-level {name} block")


def replace_top_level_block(text: str, donor: str, name: str) -> str:
    target_start, _, target_end = top_level_block_span(text, name)
    donor_start, _, donor_end = top_level_block_span(donor, name)
    return text[:target_start] + donor[donor_start:donor_end] + text[target_end:]


def named_object_group_blocks(text: str) -> list[tuple[int, int, str, str]]:
    """Return character spans, names, and text for compact objectGroups blocks."""
    blocks: list[tuple[int, int, str, str]] = []
    lines = text.splitlines(keepends=True)
    offset = 0
    index = 0
    while index < len(lines):
        if lines[index].strip() != "objectGroups{":
            offset += len(lines[index])
            index += 1
            continue
        start = offset
        depth = 0
        block_lines: list[str] = []
        while index < len(lines):
            line = lines[index]
            block_lines.append(line)
            depth += line.count("{") - line.count("}")
            offset += len(line)
            index += 1
            if depth == 0:
                break
        block = "".join(block_lines)
        match = re.search(r'(?m)^\s*name:t="([^"]+)"$', block)
        if not match:
            raise ValueError("objectGroups block has no name")
        blocks.append((start, offset, match.group(1), block))
    return blocks


def set_player_respawn_delay(text: str, seconds: int) -> str:
    text, count = re.subn(
        r"(?m)^(\s*afterRespawnDelaySec:i=)\d+$",
        rf"\g<1>{seconds}",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError("Could not set player respawn delay")
    return text


def set_allowed_unit_type(text: str, setting: str, allowed: bool) -> str:
    text, count = re.subn(
        rf"(?m)^(\s*{re.escape(setting)}:b=)(?:yes|no)$",
        rf"\g<1>{'yes' if allowed else 'no'}",
        text,
        count=1,
    )
    if count != 1:
        raise ValueError(f"Could not set {setting}")
    return text


def enable_peaceful_player_protection(text: str) -> str:
    """Keep every player unit invisible to AI targeting and immune to damage."""
    pattern = re.compile(
        r"(?ms)^(  debug_in_multiplayer\{\n)(.*?)(^  \}\n)"
    )
    match = pattern.search(text)
    if not match:
        raise ValueError("Could not find debug_in_multiplayer protection trigger")
    block = match.group(0)
    block, enabled_count = re.subn(
        r"(?m)^(    is_enabled:b=)no$", r"\g<1>yes", block, count=1
    )
    block, period_count = re.subn(
        r"(?m)^(        time:r=)1\.0$", r"\g<1>0.25", block, count=1
    )
    if (enabled_count, period_count) != (1, 1):
        raise ValueError("Could not enable recurring peaceful player protection")
    if 'object:t="all_players_squad"' not in block:
        raise ValueError("Peaceful trigger does not target all players")
    if "targetableByAi:b=no" not in block or "isImmortal:b=yes" not in block:
        raise ValueError("Peaceful trigger lacks required player protections")
    return text[: match.start()] + block + text[match.end() :]


def limit_missile_ship_engagements(text: str, distance: float) -> str:
    """Add a mission-level engagement cap to every missile escort ship."""
    lines = text.splitlines(keepends=True)
    output: list[str] = []
    index = 0
    modified = 0
    overlay = (
        "      custom_gun_properties{\n"
        f"        custom_gun_properties__aimMaxDist:r={distance:.1f}\n"
        f"        custom_gun_properties__attackMaxDist:r={distance:.1f}\n"
        "      }\n"
    )
    while index < len(lines):
        if lines[index] != "  ships{\n":
            output.append(lines[index])
            index += 1
            continue
        block_lines: list[str] = []
        depth = 0
        while index < len(lines):
            line = lines[index]
            block_lines.append(line)
            depth += line.count("{") - line.count("}")
            index += 1
            if depth == 0:
                break
        block = "".join(block_lines)
        if "rocket_naval" in block:
            if "custom_gun_properties{" in block:
                raise ValueError("Missile ship already has a custom gun overlay")
            marker = "    additionalEcsTemplates{\n"
            if marker not in block:
                raise ValueError("Missile ship has no additionalEcsTemplates block")
            block = block.replace(marker, marker + overlay, 1)
            modified += 1
        output.append(block)
    if modified != 48:
        raise ValueError(f"Expected 48 missile ships, modified {modified}")
    return "".join(output)


def add_airfield_air_spawns(
    text: str,
    placement_by_suffix: dict[str, tuple[float, float]],
    main_forward_suffixes: tuple[str, ...] = (),
    main_forward_fraction: float = 0.5,
) -> str:
    """Add one rear-offset airborne respawn point for each listed airfield."""
    groups = {name: block for _, _, name, block in named_object_group_blocks(text)}

    def position(name: str) -> tuple[float, float, float]:
        block = groups[name]
        match = re.search(
            r"tm:m=\[\[[^\]]+\] \[[^\]]+\] \[[^\]]+\] \[([^\]]+)\]\]",
            block,
        )
        if not match:
            raise ValueError(f"Could not read transform for {name}")
        x, y, z = (float(value.strip()) for value in match.group(1).split(","))
        return x, y, z

    area_blocks: list[str] = []
    respawn_actions: list[str] = []
    for team_number, team_letter, opponent_number in ((1, "A", 2), (2, "B", 1)):
        enemy_x, _, enemy_z = position(f"t{opponent_number}_airfield_main")
        main_x, _, main_z = position(f"t{team_number}_airfield_main")
        if main_forward_suffixes:
            forward_positions = [
                position(f"t{team_number}_airfield_{suffix}")
                for suffix in main_forward_suffixes
            ]
            forward_mid_x = sum(pos[0] for pos in forward_positions) / len(
                forward_positions
            )
            forward_mid_z = sum(pos[2] for pos in forward_positions) / len(
                forward_positions
            )
        for suffix, (altitude, rear_offset) in placement_by_suffix.items():
            field_name = f"t{team_number}_airfield_{suffix}"
            field_x, _, field_z = position(field_name)
            if suffix == "main" and main_forward_suffixes:
                field_x = main_x + (forward_mid_x - main_x) * main_forward_fraction
                field_z = main_z + (forward_mid_z - main_z) * main_forward_fraction
            dx = enemy_x - field_x
            dz = enemy_z - field_z
            length = math.hypot(dx, dz)
            forward_x = dx / length
            forward_z = dz / length
            spawn_x = field_x - forward_x * rear_offset
            spawn_z = field_z - forward_z * rear_offset
            area_name = f"{field_name}_air_spawn"
            radius = 200.0
            area_blocks.append(
                f"  {area_name}{{\n"
                '    type:t="Sphere"\n'
                f"    tm:m=[[{forward_x * radius:.6f}, 0.0, {forward_z * radius:.6f}] "
                "[0.0, 50.0, 0.0] "
                f"[{-forward_z * radius:.6f}, 0.0, {forward_x * radius:.6f}] "
                f"[{spawn_x:.3f}, {altitude:.1f}, {spawn_z:.3f}]]\n"
                "    objLayer:i=0\n"
                "    props{\n\n"
                "    }\n"
                "  }\n"
            )
            field_label = "Main" if suffix == "main" else f"Field {int(suffix)}"
            respawn_actions.append(
                "      missionMarkAsRespawnPoint{\n"
                f'        loc_name:t="Air Spawn · {field_label} · {altitude / 1000:g} km"\n'
                "        radius:r=-1.0\n"
                f'        target:t="{area_name}"\n'
                f'        team:t="{team_letter}"\n'
                "        isStrictPosAndDir:b=yes\n"
                "        offset:p3=0.0, 0.0, 0.0\n"
                "        tags{\n"
                "          air:b=yes\n"
                "          type_longrange_bomber:b=no\n"
                "          tank:b=no\n"
                "          ship:b=no\n"
                "        }\n"
                "      }\n"
            )

    _, _, areas_end = top_level_block_span(text, "areas")
    text = text[: areas_end - 2] + "".join(area_blocks) + text[areas_end - 2 :]

    trigger = (
        "  create_airfield_air_spawns{\n"
        "    is_enabled:b=yes\n"
        '    comments:t=""\n'
        "    props{\n"
        '      actionsType:t="PERFORM_ONE_BY_ONE"\n'
        '      conditionsType:t="ALL"\n'
        "      enableAfterComplete:b=no\n"
        "    }\n"
        "    events{\n"
        "      initMission{\n\n"
        "      }\n"
        "    }\n"
        "    conditions{\n\n"
        "    }\n"
        "    actions{\n"
        + "".join(respawn_actions)
        + "    }\n"
        "    else_actions{\n\n"
        "    }\n"
        "  }\n"
    )
    _, _, triggers_end = top_level_block_span(text, "triggers")
    return text[: triggers_end - 2] + trigger + text[triggers_end - 2 :]


def add_frontal_helicopter_spawns(
    text: str,
    field_suffixes: tuple[str, ...] = ("01", "02", "03"),
    height_above_field: float = 300.0,
    rear_offset: float = 2000.0,
) -> str:
    """Add low helicopter-only spawns behind each frontal airfield."""
    groups = {name: block for _, _, name, block in named_object_group_blocks(text)}

    def position(name: str) -> tuple[float, float, float]:
        block = groups[name]
        match = re.search(
            r"tm:m=\[\[[^\]]+\] \[[^\]]+\] \[[^\]]+\] \[([^\]]+)\]\]",
            block,
        )
        if not match:
            raise ValueError(f"Could not read transform for {name}")
        return tuple(float(value.strip()) for value in match.group(1).split(","))

    area_blocks: list[str] = []
    respawn_actions: list[str] = []
    for team_number, team_letter, opponent_number in ((1, "A", 2), (2, "B", 1)):
        enemy_x, _, enemy_z = position(f"t{opponent_number}_airfield_main")
        for suffix in field_suffixes:
            field_name = f"t{team_number}_airfield_{suffix}"
            field_x, field_y, field_z = position(field_name)
            dx = enemy_x - field_x
            dz = enemy_z - field_z
            length = math.hypot(dx, dz)
            forward_x = dx / length
            forward_z = dz / length
            spawn_x = field_x - forward_x * rear_offset
            spawn_y = field_y + height_above_field
            spawn_z = field_z - forward_z * rear_offset
            area_name = f"{field_name}_helicopter_spawn"
            radius = 120.0
            area_blocks.append(
                f"  {area_name}{{\n"
                '    type:t="Sphere"\n'
                f"    tm:m=[[{forward_x * radius:.6f}, 0.0, {forward_z * radius:.6f}] "
                "[0.0, 35.0, 0.0] "
                f"[{-forward_z * radius:.6f}, 0.0, {forward_x * radius:.6f}] "
                f"[{spawn_x:.3f}, {spawn_y:.1f}, {spawn_z:.3f}]]\n"
                "    objLayer:i=0\n"
                "    props{\n\n"
                "    }\n"
                "  }\n"
            )
            respawn_actions.append(
                "      missionMarkAsRespawnPoint{\n"
                f'        loc_name:t="Helicopter Spawn · Field {int(suffix)} · 300 m AGL"\n'
                "        radius:r=-1.0\n"
                f'        target:t="{area_name}"\n'
                f'        team:t="{team_letter}"\n'
                "        isStrictPosAndDir:b=yes\n"
                "        offset:p3=0.0, 0.0, 0.0\n"
                "        tags{\n"
                "          air:b=no\n"
                "          helicopter:b=yes\n"
                "          tank:b=no\n"
                "          ship:b=no\n"
                "          boat:b=no\n"
                "        }\n"
                "      }\n"
            )

    _, _, areas_end = top_level_block_span(text, "areas")
    text = text[: areas_end - 2] + "".join(area_blocks) + text[areas_end - 2 :]
    trigger = (
        "  create_frontal_helicopter_spawns{\n"
        "    is_enabled:b=yes\n"
        '    comments:t=""\n'
        "    props{\n"
        '      actionsType:t="PERFORM_ONE_BY_ONE"\n'
        '      conditionsType:t="ALL"\n'
        "      enableAfterComplete:b=no\n"
        "    }\n"
        "    events{\n"
        "      initMission{\n\n"
        "      }\n"
        "    }\n"
        "    conditions{\n\n"
        "    }\n"
        "    actions{\n"
        + "".join(respawn_actions)
        + "    }\n"
        "    else_actions{\n\n"
        "    }\n"
        "  }\n"
    )
    _, _, triggers_end = top_level_block_span(text, "triggers")
    return text[: triggers_end - 2] + trigger + text[triggers_end - 2 :]


def add_carrier_forward_naval_spawns(
    text: str, forward_offset: float = 3000.0
) -> str:
    """Add two ship/boat spawns per team ahead of the initial carriers."""
    carrier_transforms: dict[str, tuple[float, float, float, float]] = {}
    pattern = re.compile(
        r'(?ms)^  ships\{\n    name:t="(t[12]_aircraftcarrier_0[12])"\n'
        r"    tm:m=\[\[([^\]]+)\] \[[^\]]+\] \[[^\]]+\] \[([^\]]+)\]\]"
    )
    for match in pattern.finditer(text):
        forward_x, _, forward_z = (
            float(value.strip()) for value in match.group(2).split(",")
        )
        x, _, z = (float(value.strip()) for value in match.group(3).split(","))
        carrier_transforms[match.group(1)] = (forward_x, forward_z, x, z)
    if len(carrier_transforms) != 4:
        raise ValueError(f"Expected four carrier transforms, got {len(carrier_transforms)}")

    area_blocks: list[str] = []
    respawn_actions: list[str] = []
    for team_number, team_letter in ((1, "A"), (2, "B")):
        for carrier_number in (1, 2):
            carrier_name = f"t{team_number}_aircraftcarrier_{carrier_number:02d}"
            forward_x, forward_z, carrier_x, carrier_z = carrier_transforms[carrier_name]
            length = math.hypot(forward_x, forward_z)
            forward_x /= length
            forward_z /= length
            spawn_x = carrier_x + forward_x * forward_offset
            spawn_z = carrier_z + forward_z * forward_offset
            area_name = f"{carrier_name}_naval_spawn"
            radius = 650.0
            area_blocks.append(
                f"  {area_name}{{\n"
                '    type:t="Sphere"\n'
                f"    tm:m=[[{forward_x * radius:.6f}, 0.0, {forward_z * radius:.6f}] "
                "[0.0, 50.0, 0.0] "
                f"[{-forward_z * radius:.6f}, 0.0, {forward_x * radius:.6f}] "
                f"[{spawn_x:.3f}, 0.0, {spawn_z:.3f}]]\n"
                "    objLayer:i=0\n"
                "    props{\n\n"
                "    }\n"
                "  }\n"
            )
            respawn_actions.append(
                "      missionMarkAsRespawnPoint{\n"
                f'        loc_name:t="Naval Spawn · Carrier {carrier_number}"\n'
                "        radius:r=-1.0\n"
                f'        target:t="{area_name}"\n'
                f'        team:t="{team_letter}"\n'
                "        isStrictPosAndDir:b=yes\n"
                "        offset:p3=0.0, 0.0, 0.0\n"
                "        tags{\n"
                "          air:b=no\n"
                "          helicopter:b=no\n"
                "          tank:b=no\n"
                "          ship:b=yes\n"
                "          boat:b=yes\n"
                "        }\n"
                "      }\n"
            )

    _, _, areas_end = top_level_block_span(text, "areas")
    text = text[: areas_end - 2] + "".join(area_blocks) + text[areas_end - 2 :]
    trigger = (
        "  create_carrier_forward_naval_spawns{\n"
        "    is_enabled:b=yes\n"
        '    comments:t=""\n'
        "    props{\n"
        '      actionsType:t="PERFORM_ONE_BY_ONE"\n'
        '      conditionsType:t="ALL"\n'
        "      enableAfterComplete:b=no\n"
        "    }\n"
        "    events{\n"
        "      initMission{\n\n"
        "      }\n"
        "    }\n"
        "    conditions{\n\n"
        "    }\n"
        "    actions{\n"
        + "".join(respawn_actions)
        + "    }\n"
        "    else_actions{\n\n"
        "    }\n"
        "  }\n"
    )
    _, _, triggers_end = top_level_block_span(text, "triggers")
    return text[: triggers_end - 2] + trigger + text[triggers_end - 2 :]


def add_quick_start_package(
    text: str,
    aircraft_placements: dict[str, tuple[float, float]],
    main_forward_suffixes: tuple[str, ...],
    helicopter_fields: tuple[str, ...],
    helicopter_forward_offset: float = 8000.0,
    missile_ship_range: float = 18000.0,
    respawn_seconds: int = 30,
) -> str:
    """Apply the shared aircraft, helicopter, naval, and pacing settings."""
    text = limit_missile_ship_engagements(text, missile_ship_range)
    text = set_player_respawn_delay(text, respawn_seconds)
    text = set_allowed_unit_type(text, "isAirplanesAllowed", True)
    text = set_allowed_unit_type(text, "isHelicoptersAllowed", True)
    text = set_allowed_unit_type(text, "isShipsAllowed", True)
    text = set_allowed_unit_type(text, "isTanksAllowed", False)
    text = add_airfield_air_spawns(
        text,
        aircraft_placements,
        main_forward_suffixes=main_forward_suffixes,
    )
    text = add_frontal_helicopter_spawns(
        text,
        field_suffixes=helicopter_fields,
        height_above_field=300.0,
        rear_offset=-helicopter_forward_offset,
    )
    return add_carrier_forward_naval_spawns(text, forward_offset=3000.0)


ARCHIPELAGO_AIRSPAWNS = {
    "01": (1500.0, 6000.0),
    "02": (1500.0, 6000.0),
    "03": (1500.0, 6000.0),
    "04": (3500.0, 6000.0),
    "05": (3500.0, 6000.0),
    "main": (7000.0, 1500.0),
}


SOUTH_EASTERN_CITY_AIRSPAWNS = {
    "01": (1500.0, 6000.0),
    "02": (1500.0, 6000.0),
    "03": (3500.0, 6000.0),
    "04": (3500.0, 6000.0),
    "main": (7000.0, 1500.0),
}


def replace_named_object_groups(
    base: str, donor: str, selected_names: set[str]
) -> str:
    donor_blocks = {
        name: block for _, _, name, block in named_object_group_blocks(donor)
    }
    missing = selected_names - donor_blocks.keys()
    if missing:
        raise ValueError(f"Donor is missing object groups: {sorted(missing)}")

    output: list[str] = []
    cursor = 0
    replaced: set[str] = set()
    for start, end, name, block in named_object_group_blocks(base):
        output.append(base[cursor:start])
        if name in selected_names:
            output.append(donor_blocks[name])
            replaced.add(name)
        else:
            output.append(block)
        cursor = end
    output.append(base[cursor:])
    if replaced != selected_names:
        raise ValueError(f"Base is missing object groups: {sorted(selected_names-replaced)}")
    return "".join(output)


def flatten_southeastern_imports(text: str) -> str:
    """Embed the two internal templates required by a standalone URL mission.

    The current internal mission imports the common 64-player template and the
    1980-2018 Nuclear Escalation ship set. The already tested standalone
    Archipelago source contains those exact imports expanded by the CDK, so it
    is the canonical local source for these shared unit definitions.
    """
    if re.search(r'(?m)^\s*name:t="t1_player01"$', text):
        raise ValueError("Southeastern City source is already flattened")

    archipelago = ARCHIPELAGO_SOURCE.read_text(encoding="utf-8")
    _, arch_inner_start, arch_units_end = top_level_block_span(
        archipelago, "units"
    )
    arch_inner = archipelago[arch_inner_start : arch_units_end - 2]
    marker = '  squad{\n    name:t="t1_players_squad"\n'
    imported_start = arch_inner.find(marker)
    if imported_start < 0:
        raise ValueError("Could not locate expanded player and ship units")
    imported_units = arch_inner[imported_start:]
    imported_names = re.findall(
        r'(?m)^\s*name:t="t[12]_(?:players_squad|player\d+|aircraftcarrier_\d+|destroyer_\d+)"$',
        imported_units,
    )
    if len(imported_names) != 94:
        raise ValueError(f"Expected 94 imported unit names, got {len(imported_names)}")

    units_start, units_inner_start, units_end = top_level_block_span(text, "units")
    text = (
        text[: units_end - 2]
        + imported_units
        + text[units_end - 2 :]
    )

    imports_start, _, imports_end = top_level_block_span(text, "imports")
    text = text[:imports_start] + "imports {\n\n}\n" + text[imports_end:]
    return text


def prune_ranked_blocks(text: str, mission_rank: int) -> str:
    """Remove inactive rankRange blocks from an internal random-battle mission."""
    lines = text.splitlines(keepends=True)
    stack: list[dict[str, int | bool]] = []
    excluded: list[tuple[int, int]] = []

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.endswith("{"):
            stack.append({"start": index, "excluded": False})

        rank_match = re.fullmatch(r"rankRange:ip2\s*=\s*(-?\d+),\s*(-?\d+)", stripped)
        if rank_match:
            if not stack:
                raise ValueError("rankRange found outside a block")
            low, high = map(int, rank_match.groups())
            if not low <= mission_rank <= high:
                stack[-1]["excluded"] = True

        if stripped == "}":
            if not stack:
                raise ValueError("Unexpected closing brace while pruning ranks")
            frame = stack.pop()
            if frame["excluded"]:
                excluded.append((int(frame["start"]), index + 1))

    if stack:
        raise ValueError("Unterminated block while pruning ranks")

    excluded.sort()
    merged: list[tuple[int, int]] = []
    for start, end in excluded:
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    output: list[str] = []
    cursor = 0
    for start, end in merged:
        output.extend(lines[cursor:start])
        cursor = end
    output.extend(lines[cursor:])
    return "".join(output)


def build_southeastern_city_variants() -> None:
    source = quote_plus_sign_storage_templates(prune_ranked_blocks(
        flatten_southeastern_imports(
            SOUTHEASTERN_CITY_SOURCE.read_text(encoding="utf-8")
        ),
        mission_rank=37,
    ))

    normal = compact_scalar_syntax(set_pretty_english_metadata(
        source,
        "NORMAL",
        "All strategic and airfield defenses retain their stock behavior.",
    ))

    silent = disable_pretty_sam_channels(source)
    silent_hq11_18km = override_pretty_team1_airfields(silent, 18000.0)
    silent_hq11_18km = compact_scalar_syntax(set_pretty_english_metadata(
        silent_hq11_18km,
        "SEAD TRAINING · HQ-11 18 KM",
        "Strategic S-300 and SAMP/T sites remain targetable but cannot engage; HQ-11 sensors activate only within 18 km. Quick-start aircraft, helicopter, and naval spawns are enabled.",
    ))
    silent_hq11_18km = add_quick_start_package(
        silent_hq11_18km,
        SOUTH_EASTERN_CITY_AIRSPAWNS,
        main_forward_suffixes=("03", "04"),
        helicopter_fields=("01", "02"),
    )

    no_long_range = remove_pretty_object_groups_with_templates(
        source, ("sam_site_s300", "sam_site_sampt")
    )
    no_long_range = compact_scalar_syntax(set_pretty_english_metadata(
        no_long_range,
        "NO LONG-RANGE SAMS",
        "All 16 strategic SAM groups are removed; stock airfield defenses remain enabled. Quick-start aircraft, helicopter, and naval spawns are enabled.",
    ))
    no_long_range = add_quick_start_package(
        no_long_range,
        SOUTH_EASTERN_CITY_AIRSPAWNS,
        main_forward_suffixes=("03", "04"),
        helicopter_fields=("01", "02"),
    )

    variants = {
        "normal.blk": normal,
        "sead-training-hq11-18km.blk": silent_hq11_18km,
        "no-long-range-sams.blk": no_long_range,
    }
    for name, variant in variants.items():
        assert_balanced(variant)
        (SOUTHEASTERN_CITY_DIR / name).write_text(variant, encoding="utf-8")

    # Two-way isolation for the remote custom-room validator. If only the
    # first file fails, the new/reworked level is not accepted. If only the
    # second fails, a Southeastern mission entity or action is rejected.
    SOUTHEASTERN_DIAGNOSTICS_DIR.mkdir(exist_ok=True)
    archipelago_on_southeastern = ARCHIPELAGO_SOURCE.read_text(encoding="utf-8")
    archipelago_on_southeastern = archipelago_on_southeastern.replace(
        'level:t="levels/air_archipelago.bin"',
        'level:t="levels/air_south_eastern_city.bin"',
        1,
    )
    archipelago_on_southeastern = set_english_metadata(
        archipelago_on_southeastern,
        "DIAGNOSTIC · SOUTHEASTERN LEVEL",
        "Known-working Archipelago mission content using only the Southeastern City level.",
    )

    southeastern_on_archipelago = normal.replace(
        'level:t="levels/air_south_eastern_city.bin"',
        'level:t="levels/air_archipelago.bin"',
        1,
    )
    southeastern_on_archipelago = set_pretty_english_metadata(
        southeastern_on_archipelago,
        "DIAGNOSTIC · ARCHIPELAGO LEVEL",
        "Southeastern City mission content using only the known-working Archipelago level.",
    )

    southeastern_logic_archipelago_units = replace_top_level_block(
        normal,
        ARCHIPELAGO_SOURCE.read_text(encoding="utf-8"),
        "units",
    )
    southeastern_logic_archipelago_units = set_pretty_english_metadata(
        southeastern_logic_archipelago_units,
        "DIAGNOSTIC · ARCHIPELAGO UNITS",
        "Southeastern logic, zones, and routes with the known-working Archipelago units block.",
    )

    southeastern_nomesh_replaced = normal.replace(
        'unit_class:t="nt_assembly_area_nomesh"',
        'unit_class:t="nt_assembly_area_foundation"',
    )
    if southeastern_nomesh_replaced == normal or normal.count(
        'unit_class:t="nt_assembly_area_nomesh"'
    ) != 2:
        raise ValueError("Expected exactly two no-mesh assembly areas")
    southeastern_nomesh_replaced = set_pretty_english_metadata(
        southeastern_nomesh_replaced,
        "DIAGNOSTIC · STANDARD ASSEMBLY FOUNDATIONS",
        "Southeastern mission with only its two no-mesh assembly-area classes replaced.",
    )

    southeastern_quoted_storage_templates = set_pretty_english_metadata(
        normal,
        "DIAGNOSTIC · QUOTED STORAGE TEMPLATES",
        "Complete Southeastern mission with its eight plus-sign storage template names quoted.",
    )

    southeastern_object_names = [
        name for _, _, name, _ in named_object_group_blocks(normal)
    ]
    if len(southeastern_object_names) != 98:
        raise ValueError(
            f"Expected 98 Southeastern object groups, got {len(southeastern_object_names)}"
        )
    first_object_half = set(southeastern_object_names[:50])
    second_object_half = set(southeastern_object_names[50:])
    objects_first_half = replace_named_object_groups(
        southeastern_logic_archipelago_units, normal, first_object_half
    )
    objects_first_half = set_pretty_english_metadata(
        objects_first_half,
        "DIAGNOSTIC · OBJECTS 1-50",
        "Known-working units block with Southeastern object groups 1 through 50.",
    )
    objects_second_half = replace_named_object_groups(
        southeastern_logic_archipelago_units, normal, second_object_half
    )
    objects_second_half = set_pretty_english_metadata(
        objects_second_half,
        "DIAGNOSTIC · OBJECTS 51-98",
        "Known-working units block with Southeastern object groups 51 through 98.",
    )
    first_object_quarter = set(southeastern_object_names[:25])
    second_object_quarter = set(southeastern_object_names[25:50])
    objects_first_quarter = replace_named_object_groups(
        southeastern_logic_archipelago_units, normal, first_object_quarter
    )
    objects_first_quarter = set_pretty_english_metadata(
        objects_first_quarter,
        "DIAGNOSTIC · OBJECTS 1-25",
        "Known-working units block with Southeastern object groups 1 through 25.",
    )
    objects_second_quarter = replace_named_object_groups(
        southeastern_logic_archipelago_units, normal, second_object_quarter
    )
    objects_second_quarter = set_pretty_english_metadata(
        objects_second_quarter,
        "DIAGNOSTIC · OBJECTS 26-50",
        "Known-working units block with Southeastern object groups 26 through 50.",
    )
    first_object_eighth = set(southeastern_object_names[:12])
    second_object_eighth = set(southeastern_object_names[12:25])
    objects_first_eighth = replace_named_object_groups(
        southeastern_logic_archipelago_units, normal, first_object_eighth
    )
    objects_first_eighth = set_pretty_english_metadata(
        objects_first_eighth,
        "DIAGNOSTIC · OBJECTS 1-12",
        "Known-working units block with Southeastern object groups 1 through 12.",
    )
    objects_second_eighth = replace_named_object_groups(
        southeastern_logic_archipelago_units, normal, second_object_eighth
    )
    objects_second_eighth = set_pretty_english_metadata(
        objects_second_eighth,
        "DIAGNOSTIC · OBJECTS 13-25",
        "Known-working units block with Southeastern object groups 13 through 25.",
    )
    narrowed_object_ranges = ((1, 6), (7, 12), (13, 18), (19, 25))
    narrowed_object_variants: dict[str, str] = {}
    for first, last in narrowed_object_ranges:
        selected = set(southeastern_object_names[first - 1 : last])
        variant = replace_named_object_groups(
            southeastern_logic_archipelago_units, normal, selected
        )
        variant = set_pretty_english_metadata(
            variant,
            f"DIAGNOSTIC · OBJECTS {first}-{last}",
            f"Known-working units block with Southeastern object groups {first} through {last}.",
        )
        narrowed_object_variants[
            f"southeastern-objects-{first:02d}-{last:02d}.blk"
        ] = variant

    focused_object_ranges = ((7, 10), (11, 12), (13, 14), (15, 18))
    focused_object_variants: dict[str, str] = {}
    for first, last in focused_object_ranges:
        selected = set(southeastern_object_names[first - 1 : last])
        variant = replace_named_object_groups(
            southeastern_logic_archipelago_units, normal, selected
        )
        variant = set_pretty_english_metadata(
            variant,
            f"DIAGNOSTIC · OBJECTS {first}-{last}",
            f"Known-working units block with Southeastern object groups {first} through {last}.",
        )
        focused_object_variants[
            f"southeastern-objects-{first:02d}-{last:02d}.blk"
        ] = variant

    diagnostic_variants = {
        "archipelago-content-southeastern-level.blk": archipelago_on_southeastern,
        "southeastern-content-archipelago-level.blk": southeastern_on_archipelago,
        "southeastern-logic-archipelago-units.blk": southeastern_logic_archipelago_units,
        "southeastern-nomesh-replaced.blk": southeastern_nomesh_replaced,
        "southeastern-quoted-storage-templates.blk": southeastern_quoted_storage_templates,
        "southeastern-objects-01-50.blk": objects_first_half,
        "southeastern-objects-51-98.blk": objects_second_half,
        "southeastern-objects-01-25.blk": objects_first_quarter,
        "southeastern-objects-26-50.blk": objects_second_quarter,
        "southeastern-objects-01-12.blk": objects_first_eighth,
        "southeastern-objects-13-25.blk": objects_second_eighth,
        **narrowed_object_variants,
        **focused_object_variants,
    }
    for name, variant in diagnostic_variants.items():
        assert_balanced(variant)
        (SOUTHEASTERN_DIAGNOSTICS_DIR / name).write_text(
            variant, encoding="utf-8"
        )


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
    quick_start_no_lrsam = add_quick_start_package(
        no_lrsam,
        ARCHIPELAGO_AIRSPAWNS,
        main_forward_suffixes=("04", "05"),
        helicopter_fields=("01", "02", "03"),
    )
    write_variant(
        "no-lrsam.blk",
        set_english_metadata(
            quick_start_no_lrsam,
            "NO STRATEGIC SAMS",
            "The eight S-300 and eight SAMP/T strategic sites are removed. Quick-start aircraft, helicopter, and naval spawns are enabled.",
        ),
    )

    no_lrsam_no_airfield_aa = remove_nested_blocks(no_lrsam, "airfield_aa_2018")
    if no_lrsam_no_airfield_aa.count("airfield_aa_2018{"):
        raise ValueError("Airfield AA templates remain in no-airfield-AA variant")
    write_variant(
        "no-lrsam-no-airfield-aa.blk",
        set_english_metadata(
            no_lrsam_no_airfield_aa,
            "NO STRATEGIC SAMS / NO AIRFIELD AA",
            "Strategic SAM sites and all airfield-defense groups are removed.",
        ),
    )

    silent_lrsam = add_zero_ammo_sam_settings(source)
    if silent_lrsam.count("rearmTimeOnField:r=1000000000.0") != 16:
        raise ValueError("Not every strategic SAM launcher definition was overridden")
    write_variant(
        "silent-lrsam-experimental.blk",
        set_english_metadata(
            silent_lrsam,
            "FAILED TEST · ZERO-AMMO OVERRIDE",
            "Retained for research; the server ignores this nested ammo override.",
        ),
    )

    zero_channel_lrsam = disable_sam_channels(source)
    if zero_channel_lrsam.count("sam_site__missile_channels_max:i=0") != 16:
        raise ValueError("Not every strategic SAM site's missile channels were disabled")
    strategic_sams_silent = set_english_metadata(
        zero_channel_lrsam,
        "SEAD TRAINING · STRATEGIC SAMS SILENT",
        "Strategic S-300 and SAMP/T sites remain present but have zero engagement channels.",
    )
    write_variant(
        "sead-training-strategic-sams-silent.blk", strategic_sams_silent
    )
    # Keep the previously published URL working as a stable compatibility alias.
    write_variant(
        "silent-lrsam-zero-channels-experimental.blk", strategic_sams_silent
    )

    hq11_18km = override_team1_airfield_roster(
        zero_channel_lrsam, hq11_threat_radius=18000.0
    )
    quick_start_hq11_18km = add_quick_start_package(
        hq11_18km,
        ARCHIPELAGO_AIRSPAWNS,
        main_forward_suffixes=("04", "05"),
        helicopter_fields=("01", "02", "03"),
    )
    write_variant(
        "sead-training-hq11-18km.blk",
        set_english_metadata(
            quick_start_hq11_18km,
            "SEAD TRAINING · HQ-11 18 KM",
            "Strategic sites cannot engage; HQ-11 sensors activate only within 18 km. Quick-start aircraft, helicopter, and naval spawns are enabled.",
        ),
    )

    quick_start_experiment = add_quick_start_package(
        hq11_18km,
        ARCHIPELAGO_AIRSPAWNS,
        main_forward_suffixes=("04", "05"),
        helicopter_fields=("01", "02", "03"),
    )
    quick_start_experiment = set_english_metadata(
        quick_start_experiment,
        "EXPERIMENT · AIR + HELI + NAVAL",
        "Strategic sites are silent; HQ-11 and missile-ship engagement are capped at 18 km; player respawn is 30 seconds; aircraft, helicopter, and naval spawns are enabled.",
    )
    write_variant("experimental-quick-start-airspawns.blk", quick_start_experiment)

    short_range_experiment = override_all_direct_2018_air_defenses(
        zero_channel_lrsam,
        tunguska_radius=6000.0,
        crotale_radius=6000.0,
        pantsir_radius=8000.0,
        long_airfield_radius=18000.0,
    )
    short_range_experiment = add_quick_start_package(
        short_range_experiment,
        ARCHIPELAGO_AIRSPAWNS,
        main_forward_suffixes=("04", "05"),
        helicopter_fields=("01", "02", "03"),
    )
    short_range_experiment = set_english_metadata(
        short_range_experiment,
        "EXPERIMENT · SHORT-RANGE DEFENSES",
        "Strategic sites are silent; HQ-11 and SPYDER sensors activate within 18 km, Pantsir within 8 km, and directly configurable 2S6 and Crotale units within 6 km. Quick-start spawns are enabled.",
    )
    write_variant(
        "experimental-short-range-air-defenses.blk", short_range_experiment
    )

    peaceful_exploration = enable_peaceful_player_protection(zero_channel_lrsam)
    peaceful_exploration = add_quick_start_package(
        peaceful_exploration,
        ARCHIPELAGO_AIRSPAWNS,
        main_forward_suffixes=("04", "05"),
        helicopter_fields=("01", "02", "03"),
    )
    peaceful_exploration = set_english_metadata(
        peaceful_exploration,
        "PEACEFUL EXPLORATION",
        "All map units remain present, strategic sites have zero engagement channels, and every player vehicle is continuously hidden from AI targeting and made immortal. Quick-start aircraft, helicopter, and naval spawns are enabled.",
    )
    write_variant("peaceful-exploration.blk", peaceful_exploration)

    hq11_silent = override_team1_airfield_roster(
        zero_channel_lrsam,
        hq11_threat_radius=0.0,
        hq11_ammo=0,
        hq11_radar_managed=False,
    )
    write_variant(
        "sead-training-hq11-silent.blk",
        set_english_metadata(
            hq11_silent,
            "SEAD TRAINING · HQ-11 SILENT",
            "Strategic sites cannot engage; HQ-11 sensors and initial missile load are disabled.",
        ),
    )

    build_southeastern_city_variants()


if __name__ == "__main__":
    main()
