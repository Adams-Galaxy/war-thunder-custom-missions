#!/usr/bin/env sh
set -eu

experiment_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
game_dir=${1:-/games/SteamLibrary/steamapps/common/War Thunder}
flightmodels_dir="$game_dir/content/pkg_local/gameData/flightModels"
presets_dir="$flightmodels_dir/weaponPresets"
rocketguns_dir="$game_dir/content/pkg_local/gameData/Weapons/rocketGuns"
missions_dir="$game_dir/UserMissions"
old_missions_dir="$missions_dir/Rafale weapon experiments"
superseded_scalp_dir="$game_dir/disabled-user-missions/scalp-terminal-archive/geometry-loft-superseded"

mkdir -p "$presets_dir" "$rocketguns_dir" "$missions_dir" "$superseded_scalp_dir"

# Keep the active mission menu focused on the current comparison matrix while
# preserving the preceding native/hybrid geometry tests for later reference.
for profile in native12_45 native18_65 hybrid18_65; do
  for test_range in water ground; do
    old_test="$missions_dir/usr_wt_rafale_scalp_loft_${profile}_${test_range}_lo2.mission.blk"
    if [ -f "$old_test" ]; then
      mv "$old_test" "$superseded_scalp_dir/"
    fi
  done
done

rm -f "$old_missions_dir/southeastern-city-rafale-spice250.blk"
rm -f "$old_missions_dir/southeastern-city-rafale-brimstone.blk"
rm -f "$old_missions_dir/southeastern-city-rafale-jsow.blk"
rmdir "$old_missions_dir" 2>/dev/null || true

# Remove the superseded five-SCALP experiment names before installing the
# realistic two-station versions.
rm -f "$presets_dir/wt_rafale_m_agm84k_lo5.blk"
rm -f "$presets_dir/wt_rafale_m_agm84k_vlo5.blk"
rm -f "$missions_dir/usr_wt_rafale_agm84k_lo5.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_agm84k_vlo5.mission.blk"
# Remove the superseded high-response terminal-test filenames.
rm -f "$presets_dir/wt_rafale_m_scalp_ins_aggressive_lo2.blk"
rm -f "$presets_dir/wt_rafale_m_scalp_ins_ultralate_lo2.blk"
rm -f "$rocketguns_dir/wt_agm_84k_scalp_ins_aggressive_lo.blk"
rm -f "$rocketguns_dir/wt_agm_84k_scalp_ins_ultralate_lo.blk"
rm -f "$missions_dir/usr_wt_rafale_scalp_ins_aggressive_lo2.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_scalp_ins_ultralate_lo2.mission.blk"
# Remove the superseded terminal-profile filenames.
rm -f "$presets_dir/wt_rafale_m_scalp_ins_lo2.blk"
rm -f "$presets_dir/wt_rafale_m_scalp_ins_ultralate_damped_lo2.blk"
rm -f "$rocketguns_dir/wt_agm_84k_scalp_ins_lo.blk"
rm -f "$rocketguns_dir/wt_agm_84k_scalp_ins_ultralate_damped_lo.blk"
rm -f "$missions_dir/usr_wt_rafale_scalp_ins_lo2.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_scalp_ins_ultralate_damped_lo2.mission.blk"
# Remove the superseded compressed-pop diagnostic names.
rm -f "$presets_dir/wt_rafale_m_scalp_ins_terminal_35_400_lo2.blk"
rm -f "$presets_dir/wt_rafale_m_scalp_ins_terminal_40_500_lo2.blk"
rm -f "$rocketguns_dir/wt_agm_84k_scalp_ins_terminal_35_400_lo.blk"
rm -f "$rocketguns_dir/wt_agm_84k_scalp_ins_terminal_40_500_lo.blk"
rm -f "$missions_dir/usr_wt_rafale_scalp_ins_terminal_35_400_lo2.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_scalp_ins_terminal_40_500_lo2.mission.blk"

cp "$experiment_dir/content/pkg_local/gameData/flightModels/wt_custom_rafale_m_f3r.blk" "$flightmodels_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_spice250.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_brimstone.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_jsow.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_jsow5.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_jsow9.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm65d6.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm65g6.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm65g12.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm84h3.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm84k5.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_kh38mt4.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_kh58ushk4.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_lmur8.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm84k_lo2.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_scalp_ins_terminal_35_600_lo2.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_scalp_ins_terminal_40_1000_lo2.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_scalp_ins_ultralate_medium_lo2.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm84k_vlo2.blk" "$presets_dir/"
for profile in lead20_cap55 lead25_cap55 lead30_cap55 lead25_cap45 lead25_cap35 lead25_cap45_gain0125 lead20_cap45_gain0125 lead175_cap45_gain0125 lead15_cap45_gain0125 lead125_cap45_gain0125_damped lead10_cap45_gain0125_damped lead075_cap45_gain0125_damped; do
  cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_scalp_turn_${profile}_lo2.blk" "$presets_dir/"
done
for profile in range45 range70 hold80_35 hold200_075; do
  cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_scalp_loft_${profile}_lo2.blk" "$presets_dir/"
done
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_slam_er_lo.blk" "$rocketguns_dir/"
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_slam_er_vlo.blk" "$rocketguns_dir/"
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_scalp_ins_terminal_35_600_lo.blk" "$rocketguns_dir/"
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_scalp_ins_terminal_40_1000_lo.blk" "$rocketguns_dir/"
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_scalp_ins_ultralate_medium_lo.blk" "$rocketguns_dir/"
for profile in lead20_cap55 lead25_cap55 lead30_cap55 lead25_cap45 lead25_cap35 lead25_cap45_gain0125 lead20_cap45_gain0125 lead175_cap45_gain0125 lead15_cap45_gain0125 lead125_cap45_gain0125_damped lead10_cap45_gain0125_damped lead075_cap45_gain0125_damped; do
  cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_scalp_turn_${profile}_lo.blk" "$rocketguns_dir/"
done
for profile in range45 range70 hold80_35 hold200_075; do
  cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_scalp_loft_${profile}_lo.blk" "$rocketguns_dir/"
done
cp "$experiment_dir/UserMissions/usr_wt_rafale_spice250.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_brimstone.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_jsow.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_jsow5.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_jsow9.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm65d6.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm65g6.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm65g12.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm84h3.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm84k5.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_kh38mt4.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_kh58ushk4.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_lmur8.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm84k_lo2.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm84k_vlo2.mission.blk" "$missions_dir/"
for profile in range45 range70 hold80_35 hold200_075; do
  cp "$experiment_dir/UserMissions/usr_wt_rafale_scalp_loft_${profile}_water_lo2.mission.blk" "$missions_dir/"
  cp "$experiment_dir/UserMissions/usr_wt_rafale_scalp_loft_${profile}_ground_lo2.mission.blk" "$missions_dir/"
done
python3 "$experiment_dir/configure_localization.py" "$game_dir"

printf 'Installed Rafale weapon experiments and their HUD names in:\n  %s\n  %s\n' "$flightmodels_dir" "$missions_dir"
