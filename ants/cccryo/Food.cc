#include "State.h"
#include "Food.h"

#include <algorithm>
#include <vector>
#include <queue>

using namespace std;

Food::Food(State &state, const Location &loc) {
	location = loc; 

	vector< vector<bool> > visited(state.rows, vector<bool>(state.cols, false));
	queue<DFSLocation> frontier;
	DFSLocation frontierLoc;
	Location l, currentLoc, nextLoc;
	Square adjTile;

	visited[location.row][location.col] = true;

	for (int d = 0; d < (int)TDIRECTIONS; d++) {
		l = state.getLocation(location, d);
		visited[l.row][l.col] = true;

		if (!state.grid[l.row][l.col].isWater) {
			frontier.push(DFSLocation(l, (d + 2) % 4, 1)); 
		}
		else if (state.grid[l.row][l.col].isFood) {
			value += 20;
		}
	}

	/*
	for (int i = 0; i < state.rows; i++) {
		for (int j = 0; j < state.cols; j++) {
			state.bug << (visited[i][j] ? "1 " : "0 ");
		}
		state.bug << endl;
	}
	*/

	while (frontier.size() > 0) { 
		frontierLoc = frontier.front();
		frontier.pop();

		currentLoc = frontierLoc.loc; 
		state.bug << "Frontier expanded at " << currentLoc << endl;
		state.bug << endl;

		if (frontierLoc.dist == 10) {
			continue;
		}

		for (int d = 0; d < (int)TDIRECTIONS; d++) {
			nextLoc = state.getLocation(currentLoc, d);
			if (visited[nextLoc.row][nextLoc.col]) {
				continue;
			}
			visited[nextLoc.row][nextLoc.col] = true;
			adjTile = state.grid[nextLoc.row][nextLoc.col];
			if (adjTile.isWater || !adjTile.isVisible || adjTile.ant != -1) {
				continue;
			}
			else if (adjTile.isFood) {
				value += 20 / (frontierLoc.dist * frontierLoc.dist);
			}
			else if (adjTile.ant == 0) {
				nearby_ants.push_back(DFSLocation(currentLoc, frontierLoc.dir, frontierLoc.dist + 1));
			}

			frontier.push(DFSLocation(nextLoc, frontierLoc.dir, frontierLoc.dist + 1));
		}
	}
	return;
}

Food::~Food() {
	nearby_ants.clear();
}

Food &Food::operator=(const Food &other_food) {
	location = other_food.location;
	value = other_food.value;
	
	nearby_ants.resize(other_food.nearby_ants.size());
	copy(other_food.nearby_ants.begin(), other_food.nearby_ants.end(), nearby_ants.begin());

	return *this;
}
