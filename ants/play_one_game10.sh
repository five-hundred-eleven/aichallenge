#!/usr/bin/env sh
	./playgame.py --player_seed 42 --end_wait=0.25 --verbose -e --log_dir game_logs --turns 1000 --map_file maps/random_walk/random_walk_04p_02.map "$@" "python dist/submit/MyBot.py" "python dist/frozenants17.py" "python dist/frozenants17.py"  "python dist/frozenants9.py"
