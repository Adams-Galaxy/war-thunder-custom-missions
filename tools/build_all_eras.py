#!/usr/bin/env python3
"""Build the maintained Nuclear Escalation era matrix for both maps."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

import build_variants as core


ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "missions" / "sources"
ARCHIPELAGO_INTERNAL = SOURCES / "air_archipelago_nuclear_escalation_tdm.blk"
SHIP_SOURCES = {
    "1970": SOURCES / "nuclear_escalation_ships_1970.blk",
    "1980": SOURCES / "nuclear_escalation_ships_1980.blk",
}


@dataclass(frozen=True)
class Era:
    slug: str
    label: str
    rank: int
    ship_set: str
    strategic_templates: tuple[str, ...]
    airfield_template: str
    strongpoint_template: str
    storage_suffix: str
    ship_range: float


ERAS = (
    Era(
        "1970-early",
        "1970 Early · BR 8.7–9.7",
        26,
        "1970",
        ("sam_site_s75", "sam_site_hawk_early"),
        "airfield_aa_1970",
        "strongpoint_1970",
        "1970_early",
        12000.0,
    ),
    Era(
        "1970-late",
        "1970 Late · BR 10.0–11.0",
        30,
        "1970",
        ("sam_site_buk", "sam_site_hawk_1970"),
        "airfield_aa_1970",
        "strongpoint_1970",
        "1970_late",
        12000.0,
    ),
    Era(
        "1980",
        "1980 · BR 11.3–13.0",
        36,
        "1980",
        ("sam_site_buk_m1", "sam_site_s300", "sam_site_hawk", "sam_site_patriot"),
        "airfield_aa_1980",
        "strongpoint_1980",
        "1980",
        12000.0,
    ),
)


MAPS = {
    "archipelago": {
        "label": "Archipelago",
        "source": ARCHIPELAGO_INTERNAL,
        "output": ROOT / "missions" / "ne-archipelago-all-eras",
        "airspawns": core.ARCHIPELAGO_AIRSPAWNS,
        "main_forward_suffixes": ("04", "05"),
        "helicopter_fields": ("01", "02", "03"),
    },
    "southeastern-city": {
        "label": "Southeastern City",
        "source": core.SOUTHEASTERN_CITY_SOURCE,
        "output": ROOT / "missions" / "ne-southeastern-city-all-eras",
        "airspawns": core.SOUTH_EASTERN_CITY_AIRSPAWNS,
        "main_forward_suffixes": ("03", "04"),
        "helicopter_fields": ("01", "02"),
    },
}


SHIP_FIELDS = (
    ("unit_class", "t"),
    ("weapons", "t"),
    ("bullets0", "t"),
    ("bullets1", "t"),
    ("bullets2", "t"),
    ("bullets3", "t"),
    ("bulletsCount0", "i"),
    ("bulletsCount1", "i"),
    ("bulletsCount2", "i"),
    ("bulletsCount3", "i"),
)


def child_blocks(text: str, block_name: str) -> list[tuple[int, int, str, str]]:
    """Return named two-space child blocks from a canonical compact BLK."""
    lines = text.splitlines(keepends=True)
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    output: list[tuple[int, int, str, str]] = []
    index = 0
    opening = f"  {block_name}{{\n"
    while index < len(lines):
        if lines[index] != opening:
            index += 1
            continue
        start_index = index
        depth = 0
        while index < len(lines):
            depth += lines[index].count("{") - lines[index].count("}")
            index += 1
            if depth == 0:
                break
        block = "".join(lines[start_index:index])
        name_match = re.search(r'(?m)^    name:t="([^"]+)"$', block)
        if not name_match:
            raise ValueError(f"Unnamed {block_name} block")
        output.append((offsets[start_index], offsets[index - 1] + len(lines[index - 1]), name_match.group(1), block))
    return output


def scalar_value(block: str, field: str, kind: str) -> str:
    match = re.search(rf'(?m)^\s*{re.escape(field)}:{kind}=(.+)$', block)
    if not match:
        raise ValueError(f"Ship block lacks {field}:{kind}")
    return match.group(1)


def retarget_ship_set(text: str, ship_source: Path) -> str:
    """Keep map routes/transforms but switch every ship's era-specific payload."""
    source_text = core.compact_scalar_syntax(ship_source.read_text(encoding="utf-8"))
    source_blocks = {name: block for _, _, name, block in child_blocks(source_text, "ships")}
    target_blocks = child_blocks(text, "ships")
    target_names = {name for _, _, name, _ in target_blocks}
    if not target_names <= set(source_blocks):
        missing = ", ".join(sorted(target_names - set(source_blocks)))
        raise ValueError(f"Era ship set lacks expanded mission units: {missing}")

    output: list[str] = []
    cursor = 0
    for start, end, name, block in target_blocks:
        output.append(text[cursor:start])
        donor = source_blocks[name]
        for field, kind in SHIP_FIELDS:
            value = scalar_value(donor, field, kind)
            block, count = re.subn(
                rf'(?m)^(\s*{re.escape(field)}:{kind}=).+$',
                rf'\g<1>{value}',
                block,
                count=1,
            )
            if count != 1:
                raise ValueError(f"Could not replace {field} for {name}")
        output.append(block)
        cursor = end
    output.append(text[cursor:])
    return "".join(output)


def quote_active_storage_templates(text: str) -> str:
    text, count = re.subn(
        r'(?m)^(\s*)(fortification\+(?:fuel|ammo)_factory_[a-z0-9_]+)\{$',
        r'\1"\2"{',
        text,
    )
    if count not in {8, 12}:
        raise ValueError(f"Expected 8 or 12 storage templates, got {count}")
    return text


def build_ranked_source(source: Path, era: Era) -> str:
    text = core.compact_scalar_syntax(source.read_text(encoding="utf-8"))
    text = core.flatten_southeastern_imports(text)
    text = retarget_ship_set(text, SHIP_SOURCES[era.ship_set])
    text = core.prune_ranked_blocks(text, era.rank)
    text = quote_active_storage_templates(text)
    core.assert_balanced(text)
    return text


def set_metadata(text: str, map_label: str, era: Era, mode: str, detail: str) -> str:
    title = f"Nuclear Escalation · {map_label} · {era.label} [{mode}]"
    description = (
        f"Custom {era.label} version of the official Nuclear Escalation mission. "
        "Stars mark Soviet-aligned air defenses; crosses mark NATO. "
        + detail
    )
    text, title_count = re.subn(
        r'(?m)^(\s*)locName:t="[^"]*"$', rf'\1locName:t="{title}"', text, count=1
    )
    text, desc_count = re.subn(
        r'(?m)^(\s*)locDesc:t="[^"]*"$', rf'\1locDesc:t="{description}"', text, count=1
    )
    if (title_count, desc_count) != (1, 1):
        raise ValueError("Could not replace mission metadata")
    return text


def disable_strategic_channels(text: str, era: Era) -> str:
    alternatives = "|".join(re.escape(template) for template in era.strategic_templates)
    pattern = re.compile(rf'(?m)^(\s*)(({alternatives})\{{)$')
    matches = list(pattern.finditer(text))
    if len(matches) != 16:
        raise ValueError(f"Expected 16 {era.slug} strategic sites, got {len(matches)}")
    return pattern.sub(
        lambda match: (
            f"{match.group(1)}{match.group(2)}\n"
            f"{match.group(1)}  sam_site__missile_channels_max:i=0\n"
            f"{match.group(1)}  sam_site__target_channels_max:i=0"
        ),
        text,
    )


def unit(
    name: str,
    template: str,
    *,
    tickets: int | None = 20,
    count: int | None = None,
    radius: float | None = None,
    spawn: str | None = None,
    radar: bool = True,
    bullets: list[str] | None = None,
    ammo: list[int] | None = None,
) -> dict[str, object]:
    result: dict[str, object] = {"name": name, "templateName": template}
    if tickets is not None:
        result["death_substract_tickets"] = tickets
    if spawn is not None:
        result["spawnName"] = spawn
    if count is not None:
        result["count"] = count
    if radius is not None:
        result["threatSearchRad"] = radius
    result["dontCreateChar"] = True
    result["mods"] = ["tank_tool_kit", "manual_extinguisher"]
    if bullets is not None:
        result["bullet_names"] = bullets
    if ammo is not None:
        result["bullet_counts"] = ammo
    if not radar:
        result.pop("threatSearchRad", None)
    return result


def shilka(*, m4: bool = False, count: int | None = None, spawn: str | None = None, threat_template: bool = False) -> dict[str, object]:
    return unit(
        "ussr_zsu_23_4m4" if m4 else "ussr_zsu_23_4",
        "tank+nuclear_escalation_spaa_with_threat_radar" if threat_template else "tank+nuclear_escalation_spaa_radar_on",
        count=count,
        radius=4000.0,
        spawn=spawn,
    )


def osa(*, ammo: int, count: int | None = None, spawn: str | None = None, threat_template: bool = False) -> dict[str, object]:
    return unit(
        "ussr_9a33bm3",
        "tank+nuclear_escalation_spaa_with_threat_radar" if threat_template else "tank+nuclear_escalation_spaa_radar_on",
        count=count,
        radius=8000.0,
        spawn=spawn,
        bullets=[],
        ammo=[ammo],
    )


def m163(*, count: int | None = None, spawn: str | None = None, tank_template: bool = False) -> dict[str, object]:
    return unit(
        "us_m163_vulcan",
        "tank+nuclear_escalation_tank" if tank_template else "tank+nuclear_escalation_spaa_radar_off",
        count=count,
        spawn=spawn,
        radar=False,
    )


def roland(*, version: int, count: int | None = None, spawn: str | None = None, threat_template: bool = False) -> dict[str, object]:
    return unit(
        "germ_flarakpz_1",
        "tank+nuclear_escalation_spaa_with_threat_radar" if threat_template else "tank+nuclear_escalation_spaa_radar_on",
        count=count,
        radius=8000.0,
        spawn=spawn,
        bullets=[f"163mm_roland_{version}_aam"],
        ammo=[10],
    )


def era_airfield_roster(era: Era, army: int) -> list[dict[str, object]]:
    if era.slug.startswith("1970"):
        return [shilka(count=3), osa(ammo=4, count=3)] if army == 1 else [m163(count=3), roland(version=1, count=3)]
    if army == 1:
        return [
            osa(ammo=6, count=3),
            shilka(m4=True, count=2),
            unit("ussr_9a35_m2", "tank+nuclear_escalation_spaa_radar_off", radar=False, bullets=[], ammo=[8]),
        ]
    return [
        roland(version=3, count=3),
        unit("germ_flakpz_1a2_Gepard", "tank+nuclear_escalation_spaa_radar_on", count=3, radius=4000.0, bullets=["70mm_stinger_block2_aam"], ammo=[4]),
    ]


def ground_unit(name: str, *, count: int, bullets: list[str] | None = None) -> dict[str, object]:
    return unit(name, "tank+nuclear_escalation_tank", tickets=None, count=count, radar=False, bullets=bullets)


def era_strongpoint_roster(era: Era, army: int) -> list[dict[str, object]]:
    if era.slug.startswith("1970"):
        if army == 1:
            return [ground_unit("ussr_t_54_1951", count=3, bullets=["100mm_ussr_HEAT"]), ground_unit("ussr_bmp_1", count=2), shilka(threat_template=True)]
        return [ground_unit("us_m48a1_patton_III", count=3, bullets=["90mm_us_M431_HEAT"]), ground_unit("us_m551", count=2), m163(tank_template=True)]
    if army == 1:
        return [ground_unit("ussr_t_80u", count=3), ground_unit("ussr_bmp_2", count=2), osa(ammo=6, threat_template=True)]
    return [ground_unit("us_m1a1_abrams", count=3), ground_unit("us_m3_bradley", count=2), roland(version=3, threat_template=True)]


def era_cover_roster(template: str) -> list[dict[str, object]]:
    mapping = {
        "aa_cover_ussr_zsu_23_4": [shilka()],
        "aa_cover_ussr_9a33bm3_4_missiles": [osa(ammo=4)],
        "aa_cover_ussr_zsu_23_4m4": [shilka(m4=True)],
        "aa_cover_ussr_9a33bm3": [osa(ammo=6)],
        "aa_cover_us_m163_vulcan": [m163()],
        "aa_cover_germ_flarakpz_1_roland_1": [roland(version=1)],
        "aa_cover_germ_flarakpz_1_roland_3": [roland(version=3)],
    }
    return mapping[template]


def factory_static_roster(era: Era, army: int) -> list[dict[str, object]]:
    if era.slug == "1970-early":
        if army == 1:
            return [unit("ussr_zsu_57_2", "tank+nuclear_escalation_spaa_radar_off", spawn="spaa", radar=False), shilka(count=2, spawn="spaa")]
        return [unit("us_m42_duster", "tank+nuclear_escalation_spaa_radar_off", spawn="spaa", radar=False), m163(count=2, spawn="spaa")]
    if era.slug == "1970-late":
        return [shilka(count=2, spawn="spaa"), osa(ammo=4, spawn="spaa")] if army == 1 else [m163(count=2, spawn="spaa"), roland(version=1, spawn="spaa")]
    if army == 1:
        return [osa(ammo=6, count=2, spawn="spaa"), unit("ussr_9a35_m2", "tank+nuclear_escalation_spaa_radar_off", spawn="spaa", radar=False, bullets=[], ammo=[8])]
    return [roland(version=3, count=2, spawn="spaa"), unit("germ_flakpz_1a2_Gepard", "tank+nuclear_escalation_spaa_radar_on", spawn="spaa", radius=4000.0, bullets=["70mm_stinger_block2_aam"], ammo=[4])]


def carrier(era: Era, army: int, kind: str) -> dict[str, object]:
    if era.slug.startswith("1970"):
        suffix = "fuel" if kind == "fuel" else "awning_ammo"
        name = f"wheeled_vehicles/ussr_zil_131_{suffix}_carrier" if army == 1 else f"wheeled_vehicles/us_m35a2_{suffix}_carrier"
    else:
        if army == 1:
            name = f"wheeled_vehicles/ussr_kamaz_4310_{'fuel' if kind == 'fuel' else 'awning_ammo'}_carrier"
        else:
            name = f"wheeled_vehicles/us_{'m978_fuel' if kind == 'fuel' else 'm939_awning_ammo'}_carrier"
    return {"name": name, "templateName": "simple_tank+nuclear_escalation_tank", "count": 4}


def factory_column_roster(era: Era, army: int, kind: str) -> list[dict[str, object]]:
    if era.slug.startswith("1970"):
        defense = shilka(threat_template=True) if army == 1 else m163(tank_template=True)
    else:
        defense = osa(ammo=6, threat_template=True) if army == 1 else roland(version=3, threat_template=True)
    return [defense, carrier(era, army, kind)]


def override_all_direct_defenses(text: str, era: Era) -> str:
    cover_templates = {
        "1970-early": ("aa_cover_ussr_zsu_23_4", "aa_cover_us_m163_vulcan"),
        "1970-late": ("aa_cover_ussr_zsu_23_4", "aa_cover_ussr_9a33bm3_4_missiles", "aa_cover_us_m163_vulcan", "aa_cover_germ_flarakpz_1_roland_1"),
        "1980": ("aa_cover_ussr_zsu_23_4m4", "aa_cover_ussr_9a33bm3", "aa_cover_germ_flarakpz_1_roland_3"),
    }[era.slug]
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
        if f"      {era.airfield_template}{{\n" in block:
            marker = f"      {era.airfield_template}{{\n"
            payload = core.render_unit_settings_array("units_spawn_on_init__unitSettings:array", era_airfield_roster(era, army))
            block = block.replace(marker, marker + payload, 1)
            modified["airfield"] += 1
        elif f"      {era.strongpoint_template}{{\n" in block:
            marker = f"      {era.strongpoint_template}{{\n"
            payload = core.render_unit_settings_array("units_spawn_on_init__unitSettings:array", era_strongpoint_roster(era, army))
            block = block.replace(marker, marker + payload, 1)
            modified["strongpoint"] += 1
        else:
            cover = next((name for name in cover_templates if f"      {name}{{\n" in block), None)
            if cover:
                marker = f"      {cover}{{\n"
                payload = core.render_unit_settings_array("units_spawn_on_init__unitSettings:array", era_cover_roster(cover))
                block = block.replace(marker, marker + payload, 1)
                modified["cover"] += 1
            else:
                storage_match = re.search(rf'      "fortification\+(fuel|ammo)_factory_{re.escape(era.storage_suffix)}"\{{\n', block)
                if storage_match:
                    kind = storage_match.group(1)
                    marker = storage_match.group(0)
                    payload = core.render_unit_settings_array("units_spawn_on_init__unitSettings:array", factory_static_roster(era, army))
                    payload += core.render_unit_settings_array(f"equip_factory__columnUnitsSettings{army}:array", factory_column_roster(era, army, kind))
                    block = block.replace(marker, marker + payload, 1)
                    modified["storage"] += 1
        output.append(block)
    expected = {
        "airfield": text.count(f"      {era.airfield_template}{{\n"),
        "strongpoint": text.count(f"      {era.strongpoint_template}{{\n"),
        "cover": sum(text.count(f"      {name}{{\n") for name in cover_templates),
        "storage": len(re.findall(rf'(?m)^      "fortification\+(?:fuel|ammo)_factory_{re.escape(era.storage_suffix)}"\{{$', text)),
    }
    if modified != expected or any(value == 0 for value in expected.values()):
        raise ValueError(f"Unexpected {era.slug} easy-mode coverage: {modified}, expected {expected}")
    return "".join(output)


def add_quick_start(text: str, map_config: dict[str, object], era: Era) -> str:
    return core.add_quick_start_package(
        text,
        map_config["airspawns"],
        main_forward_suffixes=map_config["main_forward_suffixes"],
        helicopter_fields=map_config["helicopter_fields"],
        missile_ship_range=era.ship_range,
    )


def build_one_family(map_config: dict[str, object], era: Era) -> dict[str, str]:
    source = build_ranked_source(map_config["source"], era)
    map_label = str(map_config["label"])
    normal = set_metadata(source, map_label, era, "NORMAL", "All defenses retain their stock behavior.")
    silent = disable_strategic_channels(source, era)
    sead = set_metadata(
        add_quick_start(silent, map_config, era),
        map_label,
        era,
        "SEAD TRAINING",
        "All strategic batteries remain present and targetable but have zero engagement channels; era-correct shorter-range defenses remain stock. Quick-start spawns and a 30-second respawn are enabled.",
    )
    easy = set_metadata(
        add_quick_start(override_all_direct_defenses(silent, era), map_config, era),
        map_label,
        era,
        "EASY",
        "Strategic batteries are silent; directly configurable gun-AA sensors are capped at 4 km and Osa/Roland sensors at 8 km. Quick-start spawns and a 30-second respawn are enabled.",
    )
    peaceful = set_metadata(
        add_quick_start(core.enable_peaceful_player_protection(silent), map_config, era),
        map_label,
        era,
        "PEACEFUL EXPLORATION",
        "Every era-correct map unit remains present, while all players are continuously hidden from AI targeting and made immortal. Quick-start spawns are enabled.",
    )
    return {
        "normal.blk": normal,
        "sead-training.blk": sead,
        "easy.blk": easy,
        "peaceful-exploration.blk": peaceful,
    }


def build_all_era_variants() -> None:
    for map_config in MAPS.values():
        output_root = map_config["output"]
        for era in ERAS:
            family_dir = output_root / era.slug
            family_dir.mkdir(parents=True, exist_ok=True)
            for filename, text in build_one_family(map_config, era).items():
                core.assert_balanced(text)
                if len(text.encode("utf-8")) >= 512 * 1024:
                    raise ValueError(f"Remote mission exceeds 512 KiB: {family_dir / filename}")
                (family_dir / filename).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    build_all_era_variants()
