#!/usr/bin/env python3
"""Install or remove the experiment's isolated localization table."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


TABLE_NAME = "wt_custom_weapons.csv"
TABLE_LINE = f'file:t="%lang/{TABLE_NAME}"'


def read_text_raw(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return stream.read()


def write_text_raw(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(text)


def backup_once(path: Path) -> None:
    backup = path.with_name(f"{path.name}.wt-custom-missions-backup")
    if path.exists() and not backup.exists():
        shutil.copy2(path, backup)


def add_table(localization_blk: Path) -> None:
    text = read_text_raw(localization_blk)
    if TABLE_LINE in text:
        return

    loc_table = text.find("locTable{")
    if loc_table < 0:
        raise RuntimeError(f"Could not find locTable in {localization_blk}")
    closing_brace = text.find("\n}", loc_table)
    if closing_brace < 0:
        raise RuntimeError(f"Could not find the end of locTable in {localization_blk}")

    newline = "\r\n" if "\r\n" in text else "\n"
    entry = f"  {TABLE_LINE}{newline}"
    text = text[: closing_brace + 1] + entry + text[closing_brace + 1 :]
    write_text_raw(localization_blk, text)


def enable_test_localization(config_blk: Path) -> None:
    text = read_text_raw(config_blk)
    disabled = "testLocalization:b=no"
    enabled = "testLocalization:b=yes"
    if enabled in text:
        return
    if disabled not in text:
        raise RuntimeError(f"Could not find testLocalization in {config_blk}")
    write_text_raw(config_blk, text.replace(disabled, enabled, 1))


def install(game_dir: Path, source: Path) -> None:
    lang_dir = game_dir / "lang"
    localization_blk = lang_dir / "localization.blk"
    config_blk = game_dir / "config.blk"
    if not localization_blk.is_file() or not config_blk.is_file():
        raise RuntimeError("War Thunder localization/config files were not found")

    backup_once(localization_blk)
    backup_once(config_blk)
    shutil.copy2(source, lang_dir / TABLE_NAME)
    add_table(localization_blk)
    enable_test_localization(config_blk)


def remove(game_dir: Path) -> None:
    lang_dir = game_dir / "lang"
    localization_blk = lang_dir / "localization.blk"
    if localization_blk.is_file():
        lines = read_text_raw(localization_blk).splitlines(keepends=True)
        text = "".join(line for line in lines if line.strip() != TABLE_LINE)
        write_text_raw(localization_blk, text)
    (lang_dir / TABLE_NAME).unlink(missing_ok=True)
    # Do not disable testLocalization: it may be in use by the user's other
    # localization tables, including their existing weapon-name customizations.


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("game_dir", type=Path)
    parser.add_argument("--remove", action="store_true")
    args = parser.parse_args()

    if args.remove:
        remove(args.game_dir)
    else:
        source = Path(__file__).parent / "localization" / TABLE_NAME
        install(args.game_dir, source)


if __name__ == "__main__":
    main()
