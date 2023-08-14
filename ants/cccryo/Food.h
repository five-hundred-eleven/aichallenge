#ifndef _FOOD_H_
#define _FOOD_H_

#include "State.h"
#include "Ant.h"

struct Food 
{
	Food(State &, const Location &);
	~Food();

	Location location;
	int value;
	std::vector<DFSLocation> nearby_ants;

	Food &operator=(const Food &);
};

#endif
