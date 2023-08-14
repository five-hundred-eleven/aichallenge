#include "State.h"
#include "Search.h"


using namespace std;


bool LocCmp::operator()(const Location &l1, const Location &l2) const {
	return ((l1.row*4096+l1.col) < (l2.row*4096+l2.col))
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


bool cmp_dfs_targets(DFSLocation l1, DFSLocation l2) {
	return l1.dist > l2.dist;
}


void DepthFirstSearch::DepthFirstSearch(State &init_state, vector<Location> &init_start_locs, DFSType init_dfs_type)
	state(init_state), 
	s_locs(init_start_locs),
	dfs_type(init_dfs_type)
	{
	// set class variables
	visited = vector<vector<int>>(state.rows, vector<int>(state.cols, 0));
	frontier = queue<DFSLocation>();
	regions = vector<DFSRegion>();

	Location s_loc, probe;
	int next_region_key = 0;

	switch (dfs_type) {

		case DFSType.DFS_ANTS:
			for (uint s_loc_i = 0; s_loc_i < (uint)s_locs.size(); s_loc_i++) {
				s_loc = s_locs[s_loc_i];
				visited[s_loc.row][s_loc.col] = 1;
			}

			for (uint s_loc_i = 0; s_loc_i < (uint)s_locs.size(); s_loc_i++) {
				s_loc = s_locs[s_loc_i];

				for (int d=0; d<state.TDIRECTIONS; d++) {
					probe = state.getLocation(s_loc, d);
					if (!visited[probe.row][probe.col]) {
						frontier.push(DFSLocation(next_region_key, probe, 1));
						regions.push(DFSRegion(next_region_key, probe, d));	
						next_region_key++;
						visited[probe.row][probe.col] = 1;
					}
					else {
						continue;
					}
				}
			}
			break;

		case DFSType.DFS_HILLS:
			
			break;

		default:
			break;
	}
		
}

bool DepthFirstSearch::expandNode(State &state, DFSLocation &loc, queue<DFSLocation> &next_frontier) {
	Location f_loc, probe;
	Square fs;
	f_loc = loc.dfs_loc;

	for (int d = 0; d < state.TDIRECTIONS; d++) {
		probe = getLocation(f_loc, d);
		if (!visited[probe.row][probe.col]) {
			fs = State.grid[probe.row][probe.col];
			if (!fs.explored || !fs.isVisible) { // if unexplored: add to fog targets
				regions[loc.region_key].fog_targets.push(probe);
			}
			else if (fs.isWater) { // if water: do nothing
				continue;
			}
			else {
				next_frontier.push(DFSLocation(f_loc, loc.dist+1, loc.region_key));
				visited[probe.row][probe.col] = 1;
				if (fs.isFood) { // if food
					regions[loc.region_key].food_targets.push(probe);
				}
				else if (fs.ant > 0) { // if hostile ant
					regions[loc.region_key].hant_targets.push(probe);
				}
				else if (fs.isHill && hillPlayer == 0) { // if friendly hill
					regions[loc.region_key].fhill_targets.push(probe);
				}
				else if (fs.isHill && hillPlayer > 0) { // if hostile hill
					regions[loc.region_key].hhill_targets.push(probe);
				}
			}
		}
	}
}


bool DepthFirstSearch::runOnce(State &state) {
	queue<DFSLocation> next_frontier;
	DFSLocation f_loc;
	
	if (frontier.empty()) {
		return false;
	}
	while (!frontier.empty()) {
		expandNode(state, frontier.pop(), next_frontier);
	}
	frontier = next_frontier;
}


bool DepthFirstSearch::runUntil(State &state, int new_depth) {
	while (getDepth() < new_depth) {
		if (runOnce(state) == false) {
			return false;
		}
		else {
			continue;
		}
	}
}


bool DepthFirstSearch::runFull(State &state) {
	while (true) {
		if (runOnce(state) == false) {
			return false;
		}
		else {
			continue;
		}
	}
}

int DepthFirstSearch::getDepth() {
	return frontier.front().dist;
}
