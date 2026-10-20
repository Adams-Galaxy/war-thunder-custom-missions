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
    assert '"@override:WeaponSlot[5]"' in text
    assert '"@override:WeaponSlot[8]"' in text
    assert '"@override:WeaponSlot[10]"' in text
    assert '"@override:WeaponSlot[11]"' in text
    assert text.count("is_spice_250_sqr_rack.blk") == 2
    assert text.count("brimstone_dm_x3.blk") == 2
    assert text.count("BombGuns/us_agm_154a1_jsow.blk") == 3
    assert text.count("containers/bru_55_agm_154a1_jsow.blk") == 4
    assert text.count("containers/lau_88a_agm_65d_x_3.blk") == 2
    assert text.count("containers/lau_88a_agm_65g_x_3.blk") == 4
    assert text.count("rocketGuns/us_agm_84h_slam_er.blk") == 3
    assert text.count("rocketGuns/us_agm_84k_slam_er.blk") == 5
    assert text.count('preset:t="damocles"') == 2
    assert text.count('blk:t="gameData/flightModels/weaponPresets/') == 10
    assert "gameData/FlightModels/weaponPresets/" not in text
    assert text.count("{") == text.count("}")


def test_each_mission_enables_its_single_player_loadout() -> None:
    cases = {
        "usr_wt_rafale_spice250.mission.blk": "wt_rafale_m_spice250",
        "usr_wt_rafale_brimstone.mission.blk": "wt_rafale_m_brimstone",
        "usr_wt_rafale_jsow.mission.blk": "wt_rafale_m_jsow",
        "usr_wt_rafale_jsow5.mission.blk": "wt_rafale_m_jsow5",
        "usr_wt_rafale_jsow9.mission.blk": "wt_rafale_m_jsow9",
        "usr_wt_rafale_agm65d6.mission.blk": "wt_rafale_m_agm65d6",
        "usr_wt_rafale_agm65g6.mission.blk": "wt_rafale_m_agm65g6",
        "usr_wt_rafale_agm65g12.mission.blk": "wt_rafale_m_agm65g12",
        "usr_wt_rafale_agm84h3.mission.blk": "wt_rafale_m_agm84h3",
        "usr_wt_rafale_agm84k5.mission.blk": "wt_rafale_m_agm84k5",
    }

    for filename, preset in cases.items():
        text = (EXPERIMENT / "UserMissions" / filename).read_text()

        assert "peaceful_player_setup{\n    is_enabled:b=yes" in text
        assert "debug_in_multiplayer{\n    is_enabled:b=no" in text
        assert 'type:t="singleMission"' in text
        assert 'player{\n    army:i=2\n    wing:t="t2_player01"' in text
        assert "player_teamB{" not in text
        assert text.count('unit_class:t="wt_custom_rafale_m_f3r"') == 1
        assert f'weaponPreset:t="{preset}"' not in text
        assert f'weapons:t="{preset}"' in text
        if preset in {
            "wt_rafale_m_agm65d6",
            "wt_rafale_m_agm65g6",
            "wt_rafale_m_agm65g12",
            "wt_rafale_m_agm84h3",
            "wt_rafale_m_agm84k5",
        }:
            assert "fuel:r=15.0" in text
        assert 'unitWakeUp{\n        target:t="t2_player01"' in text
        assert 'unitSetProperties{\n        object:t="t2_player01"\n        targetableByAi:b=no' in text
        assert "rankRange:ip2=" not in text
        assert text.count("{") == text.count("}")


def test_presets_select_both_heavy_stations_and_talios() -> None:
    presets = EXPERIMENT / "content" / "pkg_local" / "gameData" / "flightModels" / "weaponPresets"

    for path in presets.glob("wt_rafale_m_*.blk"):
        text = path.read_text()
        assert "slot:i=3" in text
        assert "slot:i=6\n  preset:t=\"damocles\"" in text
        assert "slot:i=10" in text
        assert text.count("{") == text.count("}")


def test_multi_jsow_presets_have_expected_rack_layouts() -> None:
    presets = EXPERIMENT / "content" / "pkg_local" / "gameData" / "flightModels" / "weaponPresets"
    jsow5 = (presets / "wt_rafale_m_jsow5.blk").read_text()
    jsow9 = (presets / "wt_rafale_m_jsow9.blk").read_text()

    assert jsow5.count('preset:t="wt_jsow_x2_') == 2
    assert jsow5.count('preset:t="wt_jsow_slot7"') == 1
    assert "slot:i=4" not in jsow5
    assert "slot:i=9" not in jsow5

    assert jsow9.count('preset:t="wt_jsow_x2_') == 4
    assert jsow9.count('preset:t="wt_jsow_slot7"') == 1
    assert "slot:i=4" in jsow9
    assert "slot:i=9" in jsow9


def test_maverick_and_slam_er_presets_have_expected_layouts() -> None:
    presets = EXPERIMENT / "content" / "pkg_local" / "gameData" / "flightModels" / "weaponPresets"
    agm65d6 = (presets / "wt_rafale_m_agm65d6.blk").read_text()
    agm65g6 = (presets / "wt_rafale_m_agm65g6.blk").read_text()
    agm65g12 = (presets / "wt_rafale_m_agm65g12.blk").read_text()
    agm84h3 = (presets / "wt_rafale_m_agm84h3.blk").read_text()
    agm84k5 = (presets / "wt_rafale_m_agm84k5.blk").read_text()

    assert agm65d6.count('preset:t="wt_agm65d_x3_') == 2
    assert agm65g6.count('preset:t="wt_agm65g_x3_') == 2
    assert agm65g12.count('preset:t="wt_agm65g_x3_') == 4
    assert agm84h3.count('preset:t="wt_agm84h_') == 3
    assert agm84k5.count('preset:t="wt_agm84k_') == 5
