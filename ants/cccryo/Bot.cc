#include <set>
#include <algorithm>
#include <queue>
#include "Bot.h"
#include "Ant.h"
#include "Search.h"

using namespace std;

//constructor
Bot::Bot() {
	hill_gradient_dfs = NULL;	
};

//plays a single game of Ants.
void Bot::playGame()
{
	//reads the game parameters and sets up
	cin >> state;
	state.setup();
	endTurn();

	//continues making moves while the game is not over
	while (cin >> state)
	{
		state.updateVisionInformation();
		makeMoves();
		endTurn();
	}
};

//makes the bots moves for the turn
void Bot::makeMoves() {
 /*
 	*	I: Hill Gradient DFS
	* Perform a dfs out from friendly ant hills and establish a contour map
	* to determine how far away from hill you are
	*/
	if (hill_gradient_dfs == NULL) { // first time initialization
		*hill_gradient_dfs = new DepthFirstSearch(state, state.my_hills);
		hill_gradient_dfs->runUntil(8);
	}
	else { 
		hill_gradient_dfs->runUntil(state.turn+8);
	}
	
	/*
	 * dfs for unexplored, food, fog
	 */
	DepthFirstSearch ant_dfs(state, state.my_ants, DFSType.DFS_ANTS);
	ant_dfs.runUntil(8);

	
	 
};

//finishes the turn
void Bot::endTurn()
{
    if(state.turn > 0)
        state.reset();
    state.turn++;

    cout << "go" << endl;
};
