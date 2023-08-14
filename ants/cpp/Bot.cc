#include <set>
#include "Bot.h"
#include "Ant.h"

using namespace std;

//constructor
Bot::Bot() {

};

//plays a single game of Ants.
void Bot::playGame()
{
    //reads the game parameters and sets up
    cin >> state;
    state.setup();
    endTurn();

    //continues making moves while the game is not over
    while(cin >> state)
    {
        state.updateVisionInformation();
        makeMoves();
        endTurn();
    }
};

//makes the bots moves for the turn
void Bot::makeMoves()
{
	Square ant_tile, adj_tile;
	DFSLocation temp_dfs;
	set<Location, LocCmp> destinations, targets;
	vector<Ant> my_ants;
	int direction;
	Location dest;

	for (vector<Location>::iterator hill_it = state.myHills.begin(); hill_it != state.myHills.end(); hill_it++) {
		destinations.insert(*hill_it);
	}

    state.bug << "turn " << state.turn << ":" << endl;
    state.bug << state << endl;

    //picks out moves for each ant
    for (int ant=0; ant<(int)state.myAnts.size(); ant++) {
			my_ants.push_back(Ant(state, state.myAnts[ant]));
    }

	state.bug << "DFS and sort successful" << endl;

	for (vector<Ant>::iterator ant_it = my_ants.begin(); ant_it != my_ants.end(); ant_it++) {
		Location ant_loc = ant_it->loc;
		bool target_acquired = false;

		vector<DFSLocation> &nearbyHills = ant_it->nearby_hills;
		while (nearbyHills.size()) {
			temp_dfs = nearbyHills.back();
			nearbyHills.pop_back();
			dest = state.getLocation(ant_loc, temp_dfs.dir);
			if (destinations.find(dest) == destinations.end()) {
				state.makeMove(ant_loc, temp_dfs.dir);
				destinations.insert(dest);

				target_acquired = true;
				break;
			}
			else {
				continue;
			}
		}
		if (target_acquired) {
			continue;
		}

		vector<DFSLocation> &nearby_food = ant_it->nearby_food;
		while (nearby_food.size()) {
			temp_dfs = nearby_food.back();
			nearby_food.pop_back();
			dest = state.getLocation(ant_loc, temp_dfs.dir);
			if (destinations.find(temp_dfs.loc) == destinations.end() && destinations.find(dest) == destinations.end()) {
				state.makeMove(ant_loc, temp_dfs.dir);
				destinations.insert(dest);

				target_acquired = true;
				break;
			}
			else {
				continue;
			}
		}
		if (target_acquired) {
			continue;
		}

		vector<DFSLocation> &nearby_enemies = ant_it->nearby_enemies;
		while (nearby_food.size()) {
			temp_dfs = nearby_enemies.back();
			nearby_enemies.pop_back();
			dest = state.getLocation(ant_loc, temp_dfs.dir);
			if (destinations.find(dest) == destinations.end()) {
				state.makeMove(ant_loc, temp_dfs.dir);
				destinations.insert(dest);

				target_acquired = true;
				break;
			}
			else {
				continue;
			}
		}
		if (target_acquired) {
			continue;
		}

		vector<DFSLocation> &exploreLocs = ant_it->explore_locs;
		while (exploreLocs.size()) {
			temp_dfs = exploreLocs.back();
			exploreLocs.pop_back();
			dest = state.getLocation(ant_loc, temp_dfs.dir);
			if (destinations.find(temp_dfs.loc) == destinations.end() && destinations.find(dest) == destinations.end()) {
				state.makeMove(ant_loc, temp_dfs.dir);
				destinations.insert(dest);

				target_acquired = true;
				break;
			}
			else {
				continue;
			}
		}

	}

    state.bug << "time taken: " << state.timer.getTime() << "ms" << endl << endl;
};

//finishes the turn
void Bot::endTurn()
{
    if(state.turn > 0)
        state.reset();
    state.turn++;

    cout << "go" << endl;
};
