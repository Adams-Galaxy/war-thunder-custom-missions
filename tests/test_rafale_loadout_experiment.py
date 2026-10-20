from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "rafale-m-f3r-loadouts"
UNIT = (
    EXPERIMENT
    / "content"
    / "pkg_local"
    / "gameData"
    / "flightModels"
    / "wt_custom_rafale_m_f3r.blk"
)


def test_custom_rafale_registers_all_experimental_stores() -> None:
    text = UNIT.read_text()

    assert 'include "#/develop/gameBase/gameData/flightModels/rafale_m_f3r.blk"' in text
    assert '"@override:WeaponSlot[4]"' in text
    assert '"@override:WeaponSlot[11]"' in text
    assert text.count("is_spice_250_sqr_rack.blk") == 2
    assert text.count("brimstone_dm_x3.blk") == 2
    assert text.count("us_agm_154a1_jsow.blk") == 2
    assert text.count('preset:t="damocles"') == 2
    assert text.count("{") == text.count("}")


def test_each_mission_enables_its_single_player_loadout() -> None:
    cases = {
        "southeastern-city-rafale-spice250.blk": "wt_rafale_m_spice250",
        "southeastern-city-rafale-brimstone.blk": "wt_rafale_m_brimstone",
        "southeastern-city-rafale-jsow.blk": "wt_rafale_m_jsow",
    }

    for filename, preset in cases.items():
        text = (EXPERIMENT / "UserMissions" / filename).read_text()

        assert "debug_in_single{\n    is_enabled:b=yes" in text
        assert "debug_in_multiplayer{\n    is_enabled:b=no" in text
        assert text.count('unit_class:t="wt_custom_rafale_m_f3r"') == 2
        assert text.count(f'weaponPreset:t="{preset}"') == 2
        assert text.count("{") == text.count("}")


def test_presets_select_both_heavy_stations_and_talios() -> None:
    presets = EXPERIMENT / "content" / "pkg_local" / "gameData" / "flightModels" / "weaponPresets"

    for path in presets.glob("wt_rafale_m_*.blk"):
        text = path.read_text()
        assert "slot:i=3" in text
        assert "slot:i=6\n  preset:t=\"damocles\"" in text
        assert "slot:i=10" in text
        assert text.count("{") == text.count("}")
