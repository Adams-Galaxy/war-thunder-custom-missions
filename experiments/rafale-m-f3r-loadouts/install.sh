#!/usr/bin/env sh
set -eu

experiment_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
game_dir=${1:-/games/SteamLibrary/steamapps/common/War Thunder}
flightmodels_dir="$game_dir/content/pkg_local/gameData/flightModels"
presets_dir="$flightmodels_dir/weaponPresets"
missions_dir="$game_dir/UserMissions/Rafale weapon experiments"

mkdir -p "$presets_dir" "$missions_dir"

cp "$experiment_dir/content/pkg_local/gameData/flightModels/wt_custom_rafale_m_f3r.blk" "$flightmodels_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_spice250.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_brimstone.blk" "$presets_dir/"
cp "$experiment_dir/content/pkg_local/gameData/flightModels/weaponPresets/wt_rafale_m_jsow.blk" "$presets_dir/"
cp "$experiment_dir/UserMissions/southeastern-city-rafale-spice250.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/southeastern-city-rafale-brimstone.blk" "$missions_dir/"
cp "$experiment_dir/UserMissions/southeastern-city-rafale-jsow.blk" "$missions_dir/"

printf 'Installed Rafale weapon experiments in:\n  %s\n  %s\n' "$flightmodels_dir" "$missions_dir"
