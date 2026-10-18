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


if __name__ == "__main__":
    main()
