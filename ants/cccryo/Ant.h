#ifndef _ANT_H_
#define _ANT_H_

#include "State.h"



struct Ant
{
	Ant(State &s, Location &l);
	~Ant();

	Location loc;

	void sortTargets();
	void depthFirstSearch(State &, int depth);
	
	bool isNearFood();
	Location& nearestFood();
	void addFood(DFSLocation &);

	std::vector<DFSLocation> nearby_food;
	std::vector<DFSLocation> nearby_friendlies;
	std::vector<DFSLocation> nearby_enemies;
	std::vector<DFSLocation> nearby_hills;
	std::vector<DFSLocation> explore_locs;

	Ant &operator=(const Ant &);
};

#endif
