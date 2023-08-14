#!/usr/bin/env sh
./playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir game_logs --turns 1000 --map_file maps/maze/maze_02p_01.map "$@" "python dist/frozenants17.py" "./CryoAnts.jar"
