from pathlib import Path
import tomllib


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
SCALP_PROXY = (
    EXPERIMENT
    / "content"
    / "pkg_local"
    / "gameData"
    / "Weapons"
    / "rocketGuns"
    / "wt_agm_84k_slam_er_lo.blk"
)
SCALP_PROXY_VLO = SCALP_PROXY.with_name("wt_agm_84k_slam_er_vlo.blk")
SCALP_INS_PROXY = SCALP_PROXY.with_name("wt_agm_84k_scalp_ins_lo.blk")


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
    assert text.count("rocketGuns/su_kh_38mt.blk") == 4
    assert text.count("rocketGuns/su_kh_58ushk.blk") == 4
    assert text.count("containers/lmur_x2.blk") == 4
    assert text.count("rocketGuns/wt_agm_84k_slam_er_lo.blk") == 3
    assert text.count("rocketGuns/wt_agm_84k_slam_er_vlo.blk") == 3
    assert text.count("rocketGuns/wt_agm_84k_scalp_ins_lo.blk") == 3
    assert text.count('presetType:t="AIR_TO_GROUND"') == 3
    assert text.count('iconType:t="missile_air_to_uni_large"') >= 7
    for station_name in (
        "wt_agm84k_lo_slot3",
        "wt_scalp_ins_lo_slot3",
        "wt_agm84k_vlo_slot3",
        "wt_agm84k_lo_slot10",
        "wt_scalp_ins_lo_slot10",
        "wt_agm84k_vlo_slot10",
    ):
        station = text.split(f'name:t="{station_name}"', 1)[0].rsplit("WeaponPreset {", 1)[1]
        assert 'iconType:t="glide_bomb_default"' in station
    assert text.count('tier { idx:i=10 }') == 3
    assert text.count('tier { idx:i=2 }') == 3
    assert text.count('preset:t="damocles"') == 2
    assert text.count('blk:t="gameData/flightModels/weaponPresets/') == 16
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
        "usr_wt_rafale_kh38mt4.mission.blk": "wt_rafale_m_kh38mt4",
        "usr_wt_rafale_kh58ushk4.mission.blk": "wt_rafale_m_kh58ushk4",
        "usr_wt_rafale_lmur8.mission.blk": "wt_rafale_m_lmur8",
        "usr_wt_rafale_agm84k_lo2.mission.blk": "wt_rafale_m_agm84k_lo2",
        "usr_wt_rafale_scalp_ins_lo2.mission.blk": "wt_rafale_m_scalp_ins_lo2",
        "usr_wt_rafale_agm84k_vlo2.mission.blk": "wt_rafale_m_agm84k_vlo2",
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
            "wt_rafale_m_kh38mt4",
            "wt_rafale_m_kh58ushk4",
            "wt_rafale_m_lmur8",
            "wt_rafale_m_agm84k_lo2",
            "wt_rafale_m_scalp_ins_lo2",
            "wt_rafale_m_agm84k_vlo2",
        }:
            assert "fuel:r=15.0" in text
        assert 'unitWakeUp{\n        target:t="t2_player01"' in text
        assert 'unitSetProperties{\n        object:t="t2_player01"\n        targetableByAi:b=no' in text
        player_unit = text.split('unit_class:t="wt_custom_rafale_m_f3r"', 1)[1].split(
            "applyAllMods:b=yes", 1
        )[0]
        assert "crewSkillK:r=1.0" in player_unit
        assert "crewSkillK:r=0.0" not in player_unit
        assert (
            'name:t="t2_player01"\n'
            '    tm:m=[[-0.73315784, 0.0, -0.680058515] [0.0, 1.0, 0.0] '
            '[0.680058515, 0.0, -0.73315784] [15589.947, 1500.0, 43840.151]]'
        ) in text
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


def test_russian_missile_presets_have_expected_layouts() -> None:
    presets = EXPERIMENT / "content" / "pkg_local" / "gameData" / "flightModels" / "weaponPresets"
    kh38mt4 = (presets / "wt_rafale_m_kh38mt4.blk").read_text()
    kh58ushk4 = (presets / "wt_rafale_m_kh58ushk4.blk").read_text()
    lmur8 = (presets / "wt_rafale_m_lmur8.blk").read_text()

    assert kh38mt4.count('preset:t="wt_kh38mt_') == 4
    assert kh58ushk4.count('preset:t="wt_kh58ushk_') == 4
    assert lmur8.count('preset:t="wt_lmur_x2_') == 4
    for text in (kh38mt4, kh58ushk4, lmur8):
        assert 'slot:i=6\n  preset:t="damocles"' in text
        assert text.count("{") == text.count("}")


def test_scalp_proxies_share_physical_approximation_but_differ_in_stealth() -> None:
    lo = SCALP_PROXY.read_text()
    vlo = SCALP_PROXY_VLO.read_text()
    for text in (lo, vlo):
        assert 'include "#/develop/gameBase/gameData/Weapons/rocketGuns/us_agm_84k_slam_er.blk"' in text
        assert '"@override:rocket"' in text
        assert '"@override:mass":r=1300.0' in text
        assert '"@override:length":r=5.10' in text
        assert '"@override:machMax":r=0.95' in text
        assert '"@override:maxDistance":r=250000.0' in text
        assert '"@override:rangeMax":r=250000.0' in text
        assert '"@override:warheadMass":r=450.0' in text
        assert '"@override:explosiveType":t="pbxn_110"' in text
        assert '"@override:explosiveMass":r=250.0' in text
        assert '"@override:bulletName":t="SCALP-EG"' in text
        assert '"@override:gunnerOpticsName":t="SCALP-EG"' in text
        assert '"@override:iconType":t="guided_bomb_middle_jdam"' in text
        assert '"@override:force":r=5400.0' in text
        assert text.count("{") == text.count("}")
    assert "gunnerFilterMaxDistMult:r=0.1" in lo
    assert "gunnerFilterMaxDistMult:r=0.05" in vlo

    preset = (
        EXPERIMENT
        / "content"
        / "pkg_local"
        / "gameData"
        / "flightModels"
        / "weaponPresets"
        / "wt_rafale_m_agm84k_lo2.blk"
    ).read_text()
    assert preset.count('preset:t="wt_agm84k_lo_slot') == 2
    assert "slot:i=3" in preset
    assert "slot:i=10" in preset
    assert "slot:i=4" not in preset
    assert "slot:i=7" not in preset
    assert "slot:i=9" not in preset
    assert 'slot:i=6\n  preset:t="damocles"' in preset

    vlo_preset = (
        EXPERIMENT
        / "content"
        / "pkg_local"
        / "gameData"
        / "flightModels"
        / "weaponPresets"
        / "wt_rafale_m_agm84k_vlo2.blk"
    ).read_text()
    assert vlo_preset.count('preset:t="wt_agm84k_vlo_slot') == 2
    assert "slot:i=3" in vlo_preset
    assert "slot:i=10" in vlo_preset
    assert "slot:i=4" not in vlo_preset
    assert "slot:i=7" not in vlo_preset
    assert "slot:i=9" not in vlo_preset
    assert 'slot:i=6\n  preset:t="damocles"' in vlo_preset


def test_scalp_ins_proxy_uses_coordinate_guidance_and_damped_altitude_schedule() -> None:
    text = SCALP_INS_PROXY.read_text()

    assert 'include "#/develop/gameBase/gameData/Weapons/rocketGuns/su_grom_1.blk"' in text
    assert 'us_agm_84k_slam_er.blk' not in text
    assert '"@override:mesh":t="us_agm_84hk_slam_er_missile_na"' in text
    assert '"@override:guidanceType":t="sns"' in text
    assert 'opticalSeeker' not in text
    assert '"@override:permanentlyActivated":b=yes' in text
    assert 'inertialNavigationMandatory:b=yes' in text
    assert '"@override:designationSourceType":t="camera"' in text
    assert '"@override:constantDesignationSourceType":t="camera"' in text
    assert 'timeToHitToAltitude0:p2=0.75, 5.0' in text
    assert 'timeToHitToAltitude1:p2=2.5, 250.0' in text
    assert 'timeToHitToAltitude2:p2=4.0, 30.0' in text
    assert 'timeToHitToAltitude3:p2=6.0, 150.0' in text
    assert 'altitudeHoldTargetElevation:r=-55.0' in text
    assert 'altitudeHoldTargetOmegaMax:r=0.8' in text
    assert 'altitudeRateRateToClimb:r=0.12' in text
    assert 'climbDiffToAccelMult:r=0.0125' in text
    assert 'altitudeHoldAngleLimith:p2=-60.0, 45.0' in text
    assert '"@override:fireEffect":t=""' in text
    assert '"@override:smokeEffect":t="smoke_exhaust_air"' in text
    assert '"@override:hazeEffect":t=""' in text
    assert '"@override:propulsion1"' in text
    assert text.count('"@override:force":r=0.0') == 1
    assert '"@override:explosiveMass":r=250.0' in text
    assert 'gunnerFilterMaxDistMult:r=0.1' in text
    assert '"@override:bulletName":t="SCALP-EG"' in text
    assert '"@override:gunnerOpticsName":t="SCALP-EG"' in text
    assert '"@override:iconType":t="guided_bomb_middle_jdam"' in text
    assert text.count("{") == text.count("}")

    preset = (
        EXPERIMENT
        / "content"
        / "pkg_local"
        / "gameData"
        / "flightModels"
        / "weaponPresets"
        / "wt_rafale_m_scalp_ins_lo2.blk"
    ).read_text()
    assert preset.count('preset:t="wt_scalp_ins_lo_slot') == 2
    assert 'slot:i=3' in preset
    assert 'slot:i=10' in preset
    assert 'slot:i=6\n  preset:t="damocles"' in preset

    unit = UNIT.read_text()
    for station_name in ("wt_scalp_ins_lo_slot3", "wt_scalp_ins_lo_slot10"):
        station = unit.split(f'name:t="{station_name}"', 1)[1].split("WeaponPreset {", 1)[0]
        assert 'trigger:t="atgm"' in station
        assert 'trigger:t="guided bombs"' not in station


def test_scalp_asset_manifest_indexes_reusable_sources() -> None:
    manifest_path = ROOT / "assets" / "weapons" / "scalp-eg" / "asset.toml"
    manifest = tomllib.loads(manifest_path.read_text())

    assert manifest["schema_version"] == 1
    assert manifest["id"] == "scalp-eg"
    assert manifest["display_name"] == "SCALP-EG"
    assert manifest["ins_guidance_base"].endswith("su_grom_1.blk")
    assert manifest["integration"]["stations"] == [3, 10]
    assert manifest["integration"]["station_tiers"] == [10, 2]
    assert manifest["integration"]["projectile_icon"] == "guided_bomb_middle_jdam"
    assert manifest["integration"]["loadout_icon"] == "glide_bomb_default"
    assert {variant["id"] for variant in manifest["variants"]} == {
        "ir-lo-010",
        "ir-vlo-005",
        "ins-lo-010",
    }
    for variant in manifest["variants"]:
        for key in ("weapon", "preset", "mission"):
            assert (ROOT / variant[key]).is_file()

    ins = next(variant for variant in manifest["variants"] if variant["id"] == "ins-lo-010")
    assert ins["release_channel"] == "atgm"
    assert ins["terminal_profile_time_to_hit_s"] == [6.0, 4.0, 2.5, 0.75]
    assert ins["terminal_profile_altitude_m"] == [150.0, 30.0, 250.0, 5.0]


def test_scalp_localization_covers_every_custom_weapon_filename() -> None:
    localization = (
        EXPERIMENT / "localization" / "wt_custom_weapons.csv"
    ).read_text()

    for weapon in (
        "wt_agm_84k_slam_er_lo",
        "wt_agm_84k_slam_er_vlo",
        "wt_agm_84k_scalp_ins_lo",
    ):
        assert f'"weapons/{weapon}"' in localization
        assert f'"weapons/{weapon}/short";"SCALP-EG"' in localization

    installer = (EXPERIMENT / "install.sh").read_text()
    uninstaller = (EXPERIMENT / "uninstall.sh").read_text()
    assert 'configure_localization.py" "$game_dir"' in installer
    assert 'configure_localization.py" --remove "$game_dir"' in uninstaller
