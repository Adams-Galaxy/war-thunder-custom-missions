#!/usr/bin/env sh
set -eu

game_dir=${1:-/games/SteamLibrary/steamapps/common/War Thunder}
flightmodels_dir="$game_dir/content/pkg_local/gameData/flightModels"
presets_dir="$flightmodels_dir/weaponPresets"
missions_dir="$game_dir/UserMissions"
old_missions_dir="$missions_dir/Rafale weapon experiments"

rm -f "$flightmodels_dir/wt_custom_rafale_m_f3r.blk"
rm -f "$presets_dir/wt_rafale_m_spice250.blk"
rm -f "$presets_dir/wt_rafale_m_brimstone.blk"
rm -f "$presets_dir/wt_rafale_m_jsow.blk"
rm -f "$presets_dir/wt_rafale_m_jsow5.blk"
rm -f "$presets_dir/wt_rafale_m_jsow9.blk"
rm -f "$presets_dir/wt_rafale_m_agm65d6.blk"
rm -f "$presets_dir/wt_rafale_m_agm65g6.blk"
rm -f "$presets_dir/wt_rafale_m_agm65g12.blk"
rm -f "$presets_dir/wt_rafale_m_agm84h3.blk"
rm -f "$presets_dir/wt_rafale_m_agm84k5.blk"
rm -f "$missions_dir/usr_wt_rafale_spice250.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_brimstone.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_jsow.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_jsow5.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_jsow9.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_agm65d6.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_agm65g6.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_agm65g12.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_agm84h3.mission.blk"
rm -f "$missions_dir/usr_wt_rafale_agm84k5.mission.blk"
rm -f "$old_missions_dir/southeastern-city-rafale-spice250.blk"
rm -f "$old_missions_dir/southeastern-city-rafale-brimstone.blk"
rm -f "$old_missions_dir/southeastern-city-rafale-jsow.blk"
rmdir "$old_missions_dir" 2>/dev/null || true

printf 'Removed the Rafale weapon experiment files.\n'
