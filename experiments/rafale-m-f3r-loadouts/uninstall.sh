#!/usr/bin/env sh
set -eu

game_dir=${1:-/games/SteamLibrary/steamapps/common/War Thunder}
flightmodels_dir="$game_dir/content/pkg_local/gameData/flightModels"
presets_dir="$flightmodels_dir/weaponPresets"
missions_dir="$game_dir/UserMissions/Rafale weapon experiments"

rm -f "$flightmodels_dir/wt_custom_rafale_m_f3r.blk"
rm -f "$presets_dir/wt_rafale_m_spice250.blk"
rm -f "$presets_dir/wt_rafale_m_brimstone.blk"
rm -f "$presets_dir/wt_rafale_m_jsow.blk"
rm -f "$missions_dir/southeastern-city-rafale-spice250.blk"
rm -f "$missions_dir/southeastern-city-rafale-brimstone.blk"
rm -f "$missions_dir/southeastern-city-rafale-jsow.blk"
rmdir "$missions_dir" 2>/dev/null || true

printf 'Removed the Rafale weapon experiment files.\n'
