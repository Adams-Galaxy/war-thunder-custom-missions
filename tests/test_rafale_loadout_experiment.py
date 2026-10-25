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
KH38_TRIPLE = (
    EXPERIMENT
    / "content"
    / "pkg_local"
    / "gameData"
    / "Weapons"
    / "containers"
    / "wt_kh38mt_x3.blk"
)
SCALP_INS_TERMINAL_35_600 = SCALP_PROXY.with_name("wt_agm_84k_scalp_ins_terminal_35_600_lo.blk")
SCALP_INS_TERMINAL_40_1000 = SCALP_PROXY.with_name("wt_agm_84k_scalp_ins_terminal_40_1000_lo.blk")
SCALP_INS_ULTRALATE_MEDIUM = SCALP_PROXY.with_name("wt_agm_84k_scalp_ins_ultralate_medium_lo.blk")
SCALP_TURN_MATRIX = {
    "lead20_cap55": (2.00, 2.25, 55.0, 0.016),
    "lead25_cap55": (2.50, 2.75, 55.0, 0.016),
    "lead30_cap55": (3.00, 3.25, 55.0, 0.016),
    "lead25_cap45": (2.50, 2.75, 45.0, 0.016),
    "lead25_cap35": (2.50, 2.75, 35.0, 0.016),
    "lead25_cap45_gain0125": (2.50, 2.75, 45.0, 0.0125),
    "lead20_cap45_gain0125": (2.00, 2.25, 45.0, 0.0125),
    "lead175_cap45_gain0125": (1.75, 2.00, 45.0, 0.0125),
    "lead15_cap45_gain0125": (1.50, 1.75, 45.0, 0.0125),
    "lead125_cap45_gain0125_damped": (1.25, 1.50, 45.0, 0.0125),
    "lead10_cap45_gain0125_damped": (1.00, 1.25, 45.0, 0.0125),
    "lead075_cap45_gain0125_damped": (0.75, 1.00, 45.0, 0.0125),
}
SCALP_LOFT_MATRIX = {
    slug: ("hold", ((2.5, 700.0), (3.5, 700.0), (4.5, 500.0), (5.5, 250.0), (6.5, 40.0), (8.5, 40.0), (11.0, 80.0)))
    for slug in ("response130", "response140", "response150", "response160", "response170", "response180")
}
SCALP_LOFT_DAMPING = {
    "response130": (1.30, 0.205, 0.0195),
    "response140": (1.40, 0.205, 0.0195),
    "response150": (1.50, 0.205, 0.0195),
    "response160": (1.60, 0.205, 0.0195),
    "response170": (1.70, 0.205, 0.0195),
    "response180": (1.80, 0.205, 0.0195),
}


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
    assert text.count("rocketGuns/wt_agm_84k_slam_er_lo.blk") == 7
    assert text.count("containers/wt_kh38mt_x3.blk") == 2
    assert text.count("rocketGuns/wt_agm_84k_slam_er_vlo.blk") == 3
    assert text.count("rocketGuns/wt_agm_84k_scalp_ins_terminal_35_600_lo.blk") == 3
    assert text.count("rocketGuns/wt_agm_84k_scalp_ins_terminal_40_1000_lo.blk") == 3
    assert text.count("rocketGuns/wt_agm_84k_scalp_ins_ultralate_medium_lo.blk") == 3
    for slug in SCALP_TURN_MATRIX:
        assert text.count(f"rocketGuns/wt_agm_84k_scalp_turn_{slug}_lo.blk") == 3
    for slug in SCALP_LOFT_MATRIX:
        assert text.count(f"rocketGuns/wt_agm_84k_scalp_loft_{slug}_lo.blk") == 3
    assert text.count('presetType:t="AIR_TO_GROUND"') == 24
    assert text.count('iconType:t="missile_air_to_uni_large"') >= 7
    for station_name in (
        "wt_agm84k_lo_slot3",
        "wt_scalp_ins_terminal_35_600_lo_slot3",
        "wt_scalp_ins_terminal_40_1000_lo_slot3",
        "wt_scalp_ins_ultralate_medium_lo_slot3",
        "wt_agm84k_vlo_slot3",
        "wt_agm84k_lo_slot10",
        "wt_scalp_ins_terminal_35_600_lo_slot10",
        "wt_scalp_ins_terminal_40_1000_lo_slot10",
        "wt_scalp_ins_ultralate_medium_lo_slot10",
        *(f"wt_scalp_turn_{slug}_lo_slot{slot}" for slug in SCALP_TURN_MATRIX for slot in (3, 10)),
        *(f"wt_scalp_loft_{slug}_lo_slot{slot}" for slug in SCALP_LOFT_MATRIX for slot in (3, 10)),
        "wt_agm84k_vlo_slot10",
    ):
        station = text.split(f'name:t="{station_name}"', 1)[0].rsplit("WeaponPreset {", 1)[1]
        assert 'iconType:t="glide_bomb_default"' in station
    assert text.count('tier { idx:i=10 }') == 24
    assert text.count('tier { idx:i=2 }') == 24
    assert text.count('preset:t="damocles"') == 2
    assert text.count('blk:t="gameData/flightModels/weaponPresets/') == 37
    assert "gameData/FlightModels/weaponPresets/" not in text
    assert text.count("{") == text.count("}")


def test_peaceful_practice_loadout_and_mission() -> None:
    container = KH38_TRIPLE.read_text()
    assert 'mesh:t="lau_88a"' in container
    assert container.count('emitter:t="lau_88a_agm_65_') == 3
    assert 'blk:t="gameData/Weapons/rocketGuns/su_kh_38mt.blk"' in container
    assert "bullets:i=3" in container

    preset = (
        EXPERIMENT
        / "content/pkg_local/gameData/flightModels/weaponPresets"
        / "wt_rafale_m_practice_kh38mt6_scalp3.blk"
    ).read_text()
    assert preset.count("wt_kh38mt_x3_slot") == 2
    assert preset.count("wt_agm84k_lo_slot") == 3
    assert 'preset:t="damocles"' in preset

    mission = (
        EXPERIMENT
        / "UserMissions/usr_wt_rafale_peaceful_practice_kh38mt6_scalp3.mission.blk"
    ).read_text()
    assert 'type:t="singleMission"' in mission
    assert 'weapons:t="wt_rafale_m_practice_kh38mt6_scalp3"' in mission
    assert "maxRespawns:i=-1" in mission
    assert "afterRespawnDelaySec:i=1" in mission
    assert "isLimitedFuel:b=no" in mission
    assert "isLimitedAmmo:b=no" in mission
    assert "rearmSpeedK:r=80.0" in mission
    assert 'object:t="t2_player01"\n        targetableByAi:b=no\n        isImmortal:b=yes' in mission
    assert "debug_in_multiplayer{\n    is_enabled:b=no" in mission
    assert "rankRange:ip2=" not in mission
    assert mission.count("{") == mission.count("}")


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
        "usr_wt_rafale_scalp_ins_terminal_35_600_lo2.mission.blk": "wt_rafale_m_scalp_ins_terminal_35_600_lo2",
        "usr_wt_rafale_scalp_ins_terminal_40_1000_lo2.mission.blk": "wt_rafale_m_scalp_ins_terminal_40_1000_lo2",
        "usr_wt_rafale_scalp_ins_ultralate_medium_lo2.mission.blk": "wt_rafale_m_scalp_ins_ultralate_medium_lo2",
        "usr_wt_rafale_agm84k_vlo2.mission.blk": "wt_rafale_m_agm84k_vlo2",
    }
    cases.update(
        {
            f"usr_wt_rafale_scalp_turn_{slug}_lo2.mission.blk": f"wt_rafale_m_scalp_turn_{slug}_lo2"
            for slug in SCALP_TURN_MATRIX
        }
    )
    cases["usr_wt_rafale_scalp_turn_lead10_cap45_gain0125_damped_ground_lo2.mission.blk"] = (
        "wt_rafale_m_scalp_turn_lead10_cap45_gain0125_damped_lo2"
    )
    for slug in SCALP_LOFT_MATRIX:
        cases[f"usr_wt_rafale_scalp_loft_{slug}_ground_lo2.mission.blk"] = (
            f"wt_rafale_m_scalp_loft_{slug}_lo2"
        )

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
            "wt_rafale_m_scalp_ins_terminal_35_600_lo2",
            "wt_rafale_m_scalp_ins_terminal_40_1000_lo2",
            "wt_rafale_m_scalp_ins_ultralate_medium_lo2",
            "wt_rafale_m_agm84k_vlo2",
        } or preset.startswith(("wt_rafale_m_scalp_turn_", "wt_rafale_m_scalp_loft_")):
            assert "fuel:r=15.0" in text
        assert 'unitWakeUp{\n        target:t="t2_player01"' in text
        assert 'unitSetProperties{\n        object:t="t2_player01"\n        targetableByAi:b=no' in text
        player_unit = text.split('unit_class:t="wt_custom_rafale_m_f3r"', 1)[1].split(
            "applyAllMods:b=yes", 1
        )[0]
        assert "crewSkillK:r=1.0" in player_unit
        assert "crewSkillK:r=0.0" not in player_unit
        if filename.endswith("_ground_lo2.mission.blk"):
            assert (
                'name:t="t2_player01"\n'
                '    tm:m=[[-0.73315784, 0.0, -0.680058515] [0.0, 1.0, 0.0] '
                '[0.680058515, 0.0, -0.73315784] [15589.947, 1500.0, 43840.151]]'
            ) in text
        elif "scalp_turn_" in preset or "scalp_loft_" in preset:
            assert (
                'name:t="t2_player01"\n'
                '    tm:m=[[1.0, 0.0, 0.0] [0.0, 1.0, 0.0] '
                '[0.0, 0.0, 1.0] [40000.0, 100.0, -52000.0]]'
            ) in text
            assert text.count('name:t="scalp_water_target_left"') == 1
            assert text.count('name:t="scalp_water_target_right"') == 1
            assert '[34000.0, 0.0, -41607.695]' in text
            assert '[46000.0, 0.0, -41607.695]' in text
            assert text.count('attack_type:t="hold_fire"') == 2
        elif "scalp_ins_" in preset:
            assert (
                'name:t="t2_player01"\n'
                '    tm:m=[[1.0, 0.0, 0.0] [0.0, 1.0, 0.0] '
                '[0.0, 0.0, 1.0] [40000.0, 1500.0, -52000.0]]'
            ) in text
            assert text.count('name:t="scalp_water_target_left"') == 1
            assert text.count('name:t="scalp_water_target_right"') == 1
            assert '[34000.0, 0.0, -41607.695]' in text
            assert '[46000.0, 0.0, -41607.695]' in text
            assert text.count('attack_type:t="hold_fire"') == 2
        else:
            assert (
                'name:t="t2_player01"\n'
                '    tm:m=[[-0.73315784, 0.0, -0.680058515] [0.0, 1.0, 0.0] '
                '[0.680058515, 0.0, -0.73315784] [15589.947, 1500.0, 43840.151]]'
            ) in text
        assert "rankRange:ip2=" not in text
        assert text.count("{") == text.count("}")


def test_experiment_blks_do_not_contain_patch_markers() -> None:
    for path in EXPERIMENT.rglob("*.blk"):
        for line_number, line in enumerate(path.read_text().splitlines(), start=1):
            assert not line.startswith(("+", "-")), (
                f"{path.relative_to(ROOT)}:{line_number} contains a stray patch marker"
            )


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


def test_scalp_ins_proxy_uses_coordinate_guidance_and_staged_terminal_profiles() -> None:
    text = SCALP_INS_TERMINAL_35_600.read_text()

    assert 'include "#/develop/gameBase/gameData/Weapons/rocketGuns/su_grom_1.blk"' in text
    assert 'us_agm_84k_slam_er.blk' not in text
    assert '"@override:mesh":t="us_agm_84hk_slam_er_missile_na"' in text
    assert '"@override:guidanceType":t="sns"' in text
    assert 'opticalSeeker' not in text
    assert '"@override:permanentlyActivated":b=yes' in text
    assert 'inertialNavigationMandatory:b=yes' in text
    assert '"@override:designationSourceType":t="camera"' in text
    assert '"@override:constantDesignationSourceType":t="camera"' in text
    assert 'timeToHitToAltitude0:p2=0.95, 5.0' in text
    assert 'timeToHitToAltitude1:p2=1.20, 600.0' in text
    assert 'timeToHitToAltitude2:p2=5.0, 35.0' in text
    assert 'timeToHitToAltitude3:p2=8.0, 35.0' in text
    assert 'timeToHitToAltitude4:p2=8.5, 80.0' in text
    assert 'altitudeHoldTargetElevation:r=-75.0' in text
    assert 'altitudeHoldTargetOmegaMax:r=1.05' in text
    assert 'altitudeRateRateToClimb:r=0.15' in text
    assert 'climbDiffToAccelMult:r=0.016' in text
    assert 'altitudeHoldAngleLimith:p2=-82.0, 78.0' in text
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
        / "wt_rafale_m_scalp_ins_terminal_35_600_lo2.blk"
    ).read_text()
    assert preset.count('preset:t="wt_scalp_ins_terminal_35_600_lo_slot') == 2
    assert 'slot:i=3' in preset
    assert 'slot:i=10' in preset
    assert 'slot:i=6\n  preset:t="damocles"' in preset

    unit = UNIT.read_text()
    for station_name in (
        "wt_scalp_ins_terminal_35_600_lo_slot3",
        "wt_scalp_ins_terminal_35_600_lo_slot10",
        "wt_scalp_ins_terminal_40_1000_lo_slot3",
        "wt_scalp_ins_terminal_40_1000_lo_slot10",
        "wt_scalp_ins_ultralate_medium_lo_slot3",
        "wt_scalp_ins_ultralate_medium_lo_slot10",
        *(f"wt_scalp_turn_{slug}_lo_slot{slot}" for slug in SCALP_TURN_MATRIX for slot in (3, 10)),
    ):
        station = unit.split(f'name:t="{station_name}"', 1)[1].split("WeaponPreset {", 1)[0]
        assert 'trigger:t="atgm"' in station
        assert 'trigger:t="guided bombs"' not in station

    terminal_40_1000 = SCALP_INS_TERMINAL_40_1000.read_text()
    assert 'include "#/develop/gameBase/gameData/Weapons/rocketGuns/su_grom_1.blk"' in terminal_40_1000
    assert 'wt_agm_84k_scalp_ins_terminal_35_600_lo.blk' not in terminal_40_1000
    assert 'timeToHitToAltitude0:p2=0.75, 5.0' in terminal_40_1000
    assert 'timeToHitToAltitude1:p2=1.0, 1000.0' in terminal_40_1000
    assert 'timeToHitToAltitude2:p2=5.0, 40.0' in terminal_40_1000
    assert 'timeToHitToAltitude3:p2=8.0, 40.0' in terminal_40_1000
    assert 'timeToHitToAltitude4:p2=8.5, 80.0' in terminal_40_1000
    assert 'altitudeHoldTargetElevation:r=-80.0' in terminal_40_1000
    assert 'altitudeHoldTargetOmegaMax:r=1.05' in terminal_40_1000
    assert 'altitudeRateRateToClimb:r=0.15' in terminal_40_1000
    assert 'climbDiffToAccelMult:r=0.016' in terminal_40_1000
    assert 'altitudeHoldAngleLimith:p2=-86.0, 82.0' in terminal_40_1000

    ultralate_medium = SCALP_INS_ULTRALATE_MEDIUM.read_text()
    assert 'include "#/develop/gameBase/gameData/Weapons/rocketGuns/su_grom_1.blk"' in ultralate_medium
    assert 'wt_agm_84k_scalp_ins_terminal_35_600_lo.blk' not in ultralate_medium
    assert 'timeToHitToAltitude0:p2=0.25, 5.0' in ultralate_medium
    assert 'timeToHitToAltitude1:p2=1.1, 260.0' in ultralate_medium
    assert 'timeToHitToAltitude2:p2=4.0, 25.0' in ultralate_medium
    assert 'timeToHitToAltitude3:p2=4.5, 80.0' in ultralate_medium
    assert 'altitudeHoldTargetOmegaMax:r=1.05' in ultralate_medium
    assert 'altitudeRateRateToClimb:r=0.15' in ultralate_medium
    assert 'climbDiffToAccelMult:r=0.016' in ultralate_medium
    assert 'altitudeHoldAngleLimith:p2=-80.0, 75.0' in ultralate_medium


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
    assert manifest["test_range"]["side_length_m"] == 12000.0
    assert manifest["test_range"]["player_position_m"] == [40000.0, 1500.0, -52000.0]
    assert {variant["id"] for variant in manifest["variants"]} == {
        "ir-lo-010",
        "ir-vlo-005",
        "terminal-35-600-lo-010",
        "terminal-40-1000-lo-010",
        "ins-ultralate-medium-lo-010",
        "terminal-turn-lead20-cap55-lo-010",
        "terminal-turn-lead25-cap55-lo-010",
        "terminal-turn-lead30-cap55-lo-010",
        "terminal-turn-lead25-cap45-lo-010",
        "terminal-turn-lead25-cap35-lo-010",
        "terminal-turn-lead25-cap45-soft-lo-010",
        "terminal-turn-lead20-cap45-soft-lo-010",
        "terminal-turn-lead175-cap45-soft-lo-010",
        "terminal-turn-lead15-cap45-soft-lo-010",
        "terminal-turn-lead125-cap45-soft-damped-lo-010",
        "terminal-turn-lead10-cap45-soft-damped-lo-010",
        "terminal-turn-lead075-cap45-soft-damped-lo-010",
        "geometry-loft-native-12-45-lo-010",
        "geometry-loft-native-18-65-lo-010",
        "geometry-loft-hybrid-18-65-lo-010",
        "geometry-loft-range-45-lo-010",
        "geometry-loft-range-70-lo-010",
        "altitude-hold-80-35-control-lo-010",
        "altitude-hold-200-at-075-no-return-lo-010",
        "manual-loft-20-600-no-return-lo-010",
        "manual-loft-20-1000-no-return-lo-010",
        "manual-loft-15-600-no-return-lo-010",
        "manual-loft-15-1000-no-return-lo-010",
        "manual-loft-10-600-no-return-lo-010",
        "manual-loft-10-1000-no-return-lo-010",
        "manual-loft-600-release-10-lo-010",
        "manual-loft-600-release-15-lo-010",
        "manual-loft-1000-release-10-lo-010",
        "manual-loft-1000-release-15-lo-010",
        "manual-loft-baseline-40-lo-010",
        "manual-loft-smooth-075-lo-010",
        "manual-loft-smooth-100-lo-010",
        "manual-loft-smooth-075-damped-lo-010",
        "manual-loft-response-095-lo-010",
        "manual-loft-response-100-lo-010",
        "manual-loft-response-105-lo-010",
        "manual-loft-response-110-lo-010",
        "manual-loft-response-115-lo-010",
        "manual-loft-response-120-lo-010",
        "manual-loft-response-125-lo-010",
        "manual-loft-response-130-lo-010",
        "manual-loft-response-140-lo-010",
        "manual-loft-response-150-lo-010",
        "manual-loft-response-160-lo-010",
        "manual-loft-response-170-lo-010",
        "manual-loft-response-180-lo-010",
    }
    for variant in manifest["variants"]:
        for key in ("weapon", "preset", "mission"):
            assert (ROOT / variant[key]).is_file()

    ins = next(variant for variant in manifest["variants"] if variant["id"] == "terminal-35-600-lo-010")
    assert ins["release_channel"] == "atgm"
    assert ins["terminal_profile_time_to_hit_s"] == [8.5, 8.0, 5.0, 1.20, 0.95]
    assert ins["terminal_profile_altitude_m"] == [80.0, 35.0, 35.0, 600.0, 5.0]


def test_scalp_localization_covers_every_custom_weapon_filename() -> None:
    localization = (
        EXPERIMENT / "localization" / "wt_custom_weapons.csv"
    ).read_text()

    for weapon in (
        "wt_agm_84k_slam_er_lo",
        "wt_agm_84k_slam_er_vlo",
        "wt_agm_84k_scalp_ins_terminal_35_600_lo",
        "wt_agm_84k_scalp_ins_terminal_40_1000_lo",
        "wt_agm_84k_scalp_ins_ultralate_medium_lo",
        *(f"wt_agm_84k_scalp_turn_{slug}_lo" for slug in SCALP_TURN_MATRIX),
        *(f"wt_agm_84k_scalp_loft_{slug}_lo" for slug in SCALP_LOFT_MATRIX),
    ):
        assert f'"weapons/{weapon}"' in localization
        assert f'"weapons/{weapon}/short";"SCALP-EG"' in localization

    installer = (EXPERIMENT / "install.sh").read_text()
    uninstaller = (EXPERIMENT / "uninstall.sh").read_text()
    assert 'configure_localization.py" "$game_dir"' in installer
    assert 'configure_localization.py" --remove "$game_dir"' in uninstaller


def test_scalp_terminal_turn_matrix_is_controlled_and_complete() -> None:
    for slug, (turnover, apex, cap, gain) in SCALP_TURN_MATRIX.items():
        weapon = (SCALP_PROXY.parent / f"wt_agm_84k_scalp_turn_{slug}_lo.blk").read_text()
        preset = (
            EXPERIMENT
            / "content/pkg_local/gameData/flightModels/weaponPresets"
            / f"wt_rafale_m_scalp_turn_{slug}_lo2.blk"
        ).read_text()
        mission = (
            EXPERIMENT / "UserMissions" / f"usr_wt_rafale_scalp_turn_{slug}_lo2.mission.blk"
        ).read_text()

        assert 'include "#/develop/gameBase/gameData/Weapons/rocketGuns/su_grom_1.blk"' in weapon
        assert f"timeToHitToAltitude0:p2={turnover:.2f}, 5.0" in weapon
        assert f"timeToHitToAltitude1:p2={apex:.2f}, 600.0" in weapon
        assert "timeToHitToAltitude2:p2=6.0, 35.0" in weapon
        assert "timeToHitToAltitude3:p2=8.0, 35.0" in weapon
        assert "timeToHitToAltitude4:p2=8.5, 80.0" in weapon
        assert "timeToHitToAltitude5" not in weapon
        if slug.endswith("_damped"):
            assert "altitudeHoldTargetOmegaMax:r=0.95" in weapon
            assert "altitudeRateRateToClimb:r=0.135" in weapon
        else:
            assert "altitudeHoldTargetOmegaMax:r=1.05" in weapon
            assert "altitudeRateRateToClimb:r=0.15" in weapon
        assert f"climbDiffToAccelMult:r={gain:g}" in weapon
        assert f"altitudeHoldAngleLimith:p2=-82.0, {cap:.1f}" in weapon
        assert weapon.count("{") == weapon.count("}")

        assert preset.count(f'preset:t="wt_scalp_turn_{slug}_lo_slot') == 2
        assert f'weapons:t="wt_rafale_m_scalp_turn_{slug}_lo2"' in mission
        assert "[40000.0, 100.0, -52000.0]" in mission
        assert "tm:m=[[1.0, 0.0, 0.0] [0.0, 1.0, 0.0] [0.0, 0.0, 1.0] [40000.0, 100.0, -52000.0]]" in mission
        assert mission.count("{") == mission.count("}")


def test_scalp_geometry_loft_matrix_is_controlled_and_complete() -> None:
    for slug, (mode, parameters) in SCALP_LOFT_MATRIX.items():
        weapon = (SCALP_PROXY.parent / f"wt_agm_84k_scalp_loft_{slug}_lo.blk").read_text()
        preset = (
            EXPERIMENT
            / "content/pkg_local/gameData/flightModels/weaponPresets"
            / f"wt_rafale_m_scalp_loft_{slug}_lo2.blk"
        ).read_text()
        if mode == "range":
            near_range, near_angle, far_range, far_angle = parameters
            assert '"@override:loftEnabled":b=yes' in weapon
            assert (
                f"rangeToLoftElevation:p4={near_range:g}, {near_angle:g}, "
                f"{far_range:g}, {far_angle:g}"
            ) in weapon
            assert "loftTargetOmegaMax:r=0.95" in weapon
            assert "altitudeHoldEnabled:b=no" in weapon
            assert "timeToHitToAltitude" not in weapon
        else:
            assert '"@override:loftEnabled":b=no' in weapon
            assert "altitudeHoldEnabled:b=yes" in weapon
            for idx, (time_s, altitude_m) in enumerate(parameters):
                assert f"timeToHitToAltitude{idx}:p2={time_s:g}, {altitude_m:g}" in weapon
            assert f"timeToHitToAltitude{len(parameters)}" not in weapon
            omega, rate_gain, climb_gain = SCALP_LOFT_DAMPING[slug]
            assert f"altitudeHoldTargetOmegaMax:r={omega:g}" in weapon
            assert f"altitudeRateRateToClimb:r={rate_gain:g}" in weapon
            assert f"climbDiffToAccelMult:r={climb_gain:g}" in weapon
            assert "altitudeHoldAngleLimith:p2=-82.0, 70.0" in weapon
            altitude_lines = "\n".join(
                line for line in weapon.splitlines() if "timeToHitToAltitude" in line
            )
            assert ", 5" not in altitude_lines
            assert "p2=0," not in altitude_lines
        assert preset.count(f'preset:t="wt_scalp_loft_{slug}_lo_slot') == 2
        mission = (
            EXPERIMENT
            / "UserMissions"
            / f"usr_wt_rafale_scalp_loft_{slug}_ground_lo2.mission.blk"
        ).read_text()
        assert f'weapons:t="wt_rafale_m_scalp_loft_{slug}_lo2"' in mission
        assert ", 1500.0," in mission
        if mode == "range":
            assert "recalculates the loft angle during flight" in mission
        else:
            assert "no downward keyframe" in mission
            assert "Altitude hold releases below" in mission
        assert mission.count("{") == mission.count("}")
