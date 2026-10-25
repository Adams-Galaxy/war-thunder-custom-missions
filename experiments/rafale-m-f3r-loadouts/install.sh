#!/usr/bin/env sh
set -eu

experiment_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
game_dir=${1:-/games/SteamLibrary/steamapps/common/War Thunder}
flightmodels_dir="$game_dir/content/pkg_local/gameData/flightModels"
presets_dir="$flightmodels_dir/weaponPresets"
rocketguns_dir="$game_dir/content/pkg_local/gameData/Weapons/rocketGuns"
missions_dir="$game_dir/UserMissions"
old_missions_dir="$missions_dir/Rafale weapon experiments"

mkdir -p "$presets_dir" "$rocketguns_dir" "$missions_dir"

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
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_scalp_ins_lo2.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_agm84k_vlo2.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_slam_er_lo.blk" "$rocketguns_dir/"
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_slam_er_vlo.blk" "$rocketguns_dir/"
cp "$experiment_dir/content/pkg_local/gameData/Weapons/rocketGuns/wt_agm_84k_scalp_ins_lo.blk" "$rocketguns_dir/"
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
cp "$experiment_dir/UserMissions/usr_wt_rafale_scalp_ins_lo2.mission.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/usr_wt_rafale_agm84k_vlo2.mission.blk" "$missions_dir/"

printf 'Installed Rafale weapon experiments in:\n  %s\n  %s\n' "$flightmodels_dir" "$missions_dir"
