#ifndef __AICHALLENGE_SEARCH_H__
#define __AICHALLENGE_SEARCH_H__

#include <vector>
#include <queue>

#include "State.h"

struct LocCmp 
{
	bool operator()(const Location &, const Location &) const;
};

enum TargetType {
	EXPAND, FOG, EXPLORE, FOOD 
};

class DFSRoute
{
	
};

class DFSLocation
{
	DFSLocation(Location &dfs_loc, int dist, int region_key);

	~DFSLocation();

	Location dfs_loc;
	int dist, region_key;

	DFSLocation &operator=(DFSLocation const&);
};

class DFSRegion
{
	DFSRegion(int region_key, Location &origin_loc, int dir);

	int key, dir;
	Location origin_loc;	

	std::vector<Location> food_targets, fog_targets, fhill_targets, hhill_targets;
	std::vector<Location> fant_targets, hant_targets;
	std::vector<int> targets;
	std::set<int> neihbors;
};

enum DFSType {
	DFS_HILLS, DFS_ANTS
};

class DepthFirstSearch
{
	DepthFirstSearch(State &, std::vector<Location> &);
	~DepthFirstSearch();

	bool expandNode(State &state, DFSLocation &loc, std::queue<DFSLocation> &);

	bool runOnce(State &state): // runs a single iteration
	bool runFor(State &state, int depth_iter); // runs DFS for depth_iter iterations
	bool runUntil(State &state, int new_depth); // runs DFS until depth is new_depth
	bool runFull(State &state); // runs until stop

	int getDepth();

	std::vector<Location> &getFoodTargets();
	std::vector<Location> &getFHillTargets();
	std::vector<Location> &getHHillTargets();
	std::vector<Location> &getFAntsTargets();
	std::vector<Location> &getHAntsTargets();

	State &state;
	std::vector<Location> &s_locs;
	DFSType dfs_type;
	std::queue<DFSLocation> frontier;
	std::vector<DFSRegion> regions;
	std::vector< std::vector<bool> > visited;
};

#endif
