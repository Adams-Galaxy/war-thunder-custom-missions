#!/usr/bin/env python3
"""Build maintained Nuclear Escalation mission variants from source.blk."""

from pathlib import Path
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
    source = prune_ranked_blocks(
        flatten_southeastern_imports(
            SOUTHEASTERN_CITY_SOURCE.read_text(encoding="utf-8")
        ),
        mission_rank=37,
    )

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
        "Strategic S-300 and SAMP/T sites remain targetable but cannot engage; HQ-11 sensors activate only within 18 km.",
    ))

    no_long_range = remove_pretty_object_groups_with_templates(
        source, ("sam_site_s300", "sam_site_sampt")
    )
    no_long_range = compact_scalar_syntax(set_pretty_english_metadata(
        no_long_range,
        "NO LONG-RANGE SAMS",
        "All 16 strategic SAM groups are removed; stock airfield defenses remain enabled.",
    ))

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

    diagnostic_variants = {
        "archipelago-content-southeastern-level.blk": archipelago_on_southeastern,
        "southeastern-content-archipelago-level.blk": southeastern_on_archipelago,
        "southeastern-logic-archipelago-units.blk": southeastern_logic_archipelago_units,
        "southeastern-nomesh-replaced.blk": southeastern_nomesh_replaced,
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
    write_variant(
        "no-lrsam.blk",
        set_english_metadata(
            no_lrsam,
            "NO STRATEGIC SAMS",
            "The eight S-300 and eight SAMP/T strategic sites are removed.",
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
    write_variant(
        "sead-training-hq11-18km.blk",
        set_english_metadata(
            hq11_18km,
            "SEAD TRAINING · HQ-11 18 KM",
            "Strategic sites cannot engage; HQ-11 sensors activate only within 18 km.",
        ),
    )

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
