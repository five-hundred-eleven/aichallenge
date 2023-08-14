#ifndef BOT_H_
#define BOT_H_

#include "State.h"
#include "Search.h"

/*
    This struct represents your bot in the game of Ants
*/
struct Bot
{
    State state;
		DepthFirstSearch *hill_gradient_dfs;

    Bot();

    void playGame();    // plays a single game of Ants

    void makeMoves();   // makes moves for a single turn
    void endTurn();     // indicates to the engine that it has made its moves
};

#endif //BOT_H_
