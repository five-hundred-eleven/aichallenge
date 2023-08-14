#!/usr/bin/env sh
./playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir game_logs --turns 1000 --map_file maps/multi_hill_maze/maze_07p_01.map "$@" "python dist/frozenants12_1.py" "python dist/frozenants9.py" "python dist/frozenants8.py" "python dist/frozenants17.py" "python /home/cowley/Desktop/submit/MyBot.py" "python dist/frozenants14.py" "python dist/frozenants12_1.py" 
