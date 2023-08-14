#include <algorithm>
#include <vector>
#include <queue>
#include <set>

#include "Ant.h"

using namespace std;

bool LocCmp::operator()(const Location &l1, const Location &l2) const {
	return (l1.row != l2.row) ? (l1.row < l2.row) : (l1.col < l2.col);
}

DFSLocation::DFSLocation() {
	return;
}
DFSLocation::DFSLocation(Location &l) : loc(l) {
	return;
}

DFSLocation::DFSLocation(Location &l, int direction, int distance) 
: loc(l), dir(direction), dist(distance) {
	return;
}

DFSLocation::~DFSLocation() {
	return;
}

DFSLocation &DFSLocation::operator=(DFSLocation const& r_d) {
	this->loc = r_d.loc;
	this->dir = r_d.dir;
	this->dist = r_d.dist;

	return *this;
}

Ant::Ant(State &s, Location &l) {
	s.bug << "Creating new ant at " << l.row << ", " << l.col << endl;
	loc.row = l.row;
	loc.col = l.col;

	depthFirstSearch(s, 8);
	sortTargets();
	return;
}

Ant::~Ant() {
	nearby_food.clear();
	nearby_friendlies.clear();
	nearby_enemies.clear();
	nearby_hills.clear();

	return;
}

bool cmp_dfs_targets(DFSLocation l1, DFSLocation l2) {
	return l1.dist > l2.dist;
}

void Ant::sortTargets() {
	sort(nearby_food.begin(), nearby_food.end(), cmp_dfs_targets);
	sort(nearby_friendlies.begin(), nearby_friendlies.end(), cmp_dfs_targets);
	sort(nearby_enemies.begin(), nearby_enemies.end(), cmp_dfs_targets);
	sort(nearby_hills.begin(), nearby_hills.end(), cmp_dfs_targets);
	sort(explore_locs.begin(), explore_locs.end(), cmp_dfs_targets);
}

bool Ant::isNearFood() {
   if (nearby_food.empty()) {
		return false;
   }
   else {
		return true;
   }
}   

Location& Ant::nearestFood() {
	Location &l = nearby_food.back().loc;
	nearby_food.pop_back(); return l;
}

void Ant::addFood(DFSLocation &food_loc) {
	nearby_food.push_back(food_loc);
}

void Ant::depthFirstSearch(State &state, int depth) {
	queue<DFSLocation> frontier;
	vector< vector<bool> > visited(state.rows, vector<bool>(state.cols, false));
	Square adj_tile;
	Location l, current_loc = loc, next_loc;
	DFSLocation frontier_loc, next_frontier_loc;

	visited[current_loc.row][current_loc.col] = true;

	state.bug << "Depth first search" << endl;

	for (int d = 0; d < (int)TDIRECTIONS; d++) {
		l = state.getLocation(loc, d);
		visited[l.row][l.col] = true;

		if (!state.grid[l.row][l.col].isWater) {
			frontier.push(DFSLocation(l, d, 0)); 
		}
		else {
			continue;
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
		frontier_loc = frontier.front();
		frontier.pop();

		current_loc = frontier_loc.loc; 
		state.bug << "Frontier expanded at " << current_loc << endl;
		state.bug << endl;

		if (frontier_loc.dist == depth) {
			continue;
		}

		for (int d = 0; d < (int)TDIRECTIONS; d++) {
			next_loc = state.getLocation(current_loc, d);
			if (visited[next_loc.row][next_loc.col]) {
				state.bug << "Visited, continuing " << next_loc << (visited[next_loc.row][next_loc.col] ? "true" : "false") << endl;
				continue;
			}
			visited[next_loc.row][next_loc.col] = true;
			adj_tile = state.grid[next_loc.row][next_loc.col];

			if (!adj_tile.isVisible) {
				if (!adj_tile.explored) {
					explore_locs.push_back(DFSLocation(next_loc, frontier_loc.dir, frontier_loc.dist + 1));
				}	
				else {
					continue;
				}
			}
			else if (adj_tile.isWater) {
				continue;
			}
			else if (adj_tile.isFood) {
				nearby_food.push_back(DFSLocation(next_loc, frontier_loc.dir, frontier_loc.dist + 1));
			}
			else if (adj_tile.isHill && adj_tile.hillPlayer) {
			   	nearby_hills.push_back(DFSLocation(next_loc, frontier_loc.dir, frontier_loc.dist + 1));
			}
			else if (adj_tile.ant == 0) {
				nearby_friendlies.push_back(DFSLocation(next_loc, frontier_loc.dir, frontier_loc.dist + 1));
			}
			else if (adj_tile.ant >= 0) {
				nearby_enemies.push_back(DFSLocation(next_loc, frontier_loc.dir, frontier_loc.dist + 1));
			}

			frontier.push(DFSLocation(next_loc, frontier_loc.dir, frontier_loc.dist + 1));
		}
	}
}

Ant &Ant::operator=(const Ant &other) {
	loc.col = other.loc.col; loc.row = other.loc.row;

	nearby_food.resize(other.nearby_food.size()); 
	copy(other.nearby_food.begin(), other.nearby_food.end(), nearby_food.begin());

	nearby_friendlies.resize(other.nearby_friendlies.size()); 
	copy(other.nearby_friendlies.begin(), other.nearby_friendlies.end(), nearby_friendlies.begin());

	nearby_enemies.resize(other.nearby_enemies.size()); 
	copy(other.nearby_enemies.begin(), other.nearby_enemies.end(), nearby_enemies.begin());

	nearby_hills.resize(other.nearby_hills.size()); 
	copy(other.nearby_hills.begin(), other.nearby_hills.end(), nearby_hills.begin());

	return *this;
}
