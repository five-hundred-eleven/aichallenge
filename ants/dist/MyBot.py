#!/usr/bin/env python

from ants import *
import random
from random import randint, shuffle
import csv
from collections import namedtuple, deque, defaultdict
from math import sqrt, copysign
from bisect import insort

path_node = namedtuple('loc_node', ['parent', 'location'])
frontier_node = namedtuple('frontier_node', ['h_val', 'f_val', 'location', 'parent'])

random.seed()

logs = csv.writer(open('log_frozenants.csv', 'wb'))

AIM = {'n': (-1, 0),
        'e': (0, 1), 's': (1, 0),
        'w': (0, -1)}
RIGHT = {'n': 'e',
        'e': 's',
        's': 'w',
        'w': 'n'}
LEFT = {'n': 'w',
        'e': 'n',
        's': 'e',
        'w': 's'}
BEHIND = {'n': 's',
        's': 'n',
        'e': 'w',
        'w': 'e'}
TYPE = {'food': (130, -5),
        'fog' : (20, -2),
        'hill': (150, -5)}


class MyBot:
    def __init__(self):
        # define class level variables, will be remembered between turns
        pass

    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.row_translator = [r for r in range(ants.rows)]
        self.row_translator.extend(self.row_translator)

        self.danger = defaultdict(lambda: 0)

        self.hills = []
        self.unseen = set() 
        self.impassable = set()

        self.explore_locs = {} 
        self.explore_ghost_locs = set()
        self.explore_loc_set = False
        self.explored = set()

        self.stored_paths = {}
        self.path_dists = {}
        self.food_locs = set() 
        self.bookkeeping = []
        self.rallypoint = False
        for row in range(0, ants.rows):
            for col in range(0, ants.cols):
                self.unseen.add((row, col))

#        self.top_explore_offsets = []
#        self.bottom_explore_offsets = []
#        self.left_explore_offsets = []
#        self.right_explore_offsets = []
#
        #for d_row in range(-1, 4):
        #    for d_col in range(-1, 2):
        #        d = d_row**2 + d_col**2
        #        self.top_explore_offsets.append(
        #                ((
        #                    d,
        #                    (d_row % ants.rows) - ants.rows,
        #                    (d_col % ants.cols) - ants.cols
        #                )))
        #for d_row in range(-4, 1, -1):
        #    for d_col in range(-1, 2):
        #        d = d_row**2 + d_col**2
        #        self.bottom_explore_offsets.append(
        #                ((
        #                    d,
        #                    (d_row % ants.rows) - ants.rows,
        #                    (d_col % ants.cols) - ants.cols
        #                )))
        #for d_row in range(-1, 2):
        #    for d_col in range(-4, 1, -1):
        #        d = d_row**2 + d_col**2
        #        self.left_explore_offsets.append(
        #                ((
        #                    d,
        #                    (d_row % ants.rows) - ants.rows,
        #                    (d_col % ants.cols) - ants.cols
        #                )))
        #for d_row in range(-1, 2):
        #    for d_col in range(-1, 4):
        #        d = d_row**2 + d_col**2
        #        self.right_explore_offsets.append(
        #                ((
        #                    d,
        #                    (d_row % ants.rows) - ants.rows,
        #                    (d_col % ants.cols) - ants.cols
        #                )))

        #self.top_explore_offsets.sort()
        #self.bottom_explore_offsets.sort()
        #self.left_explore_offsets.sort()
        #self.right_explore_offsets.sort()

        #self.top_explore_offsets = map(lambda a: (a[1], a[2]), self.top_explore_offsets)
        #self.bottom_explore_offsets = map(lambda a: (a[1], a[2]), self.bottom_explore_offsets)
        #self.left_explore_offsets = map(lambda a: (a[1], a[2]), self.left_explore_offsets)
        #self.right_explore_offsets = map(lambda a: (a[1], a[2]), self.right_explore_offsets)

        self.radius_offsets = []
        self.vision_offsets = []
        self.adj_offsets = []
        mx = int(sqrt(ants.viewradius2))
        for d_row in range(-mx, mx + 1):
            for d_col in range(-mx, mx + 1):
                d = d_row**2 + d_col**2
                if d <= ants.viewradius2:
                    self.radius_offsets.append(
                            ((
                                (d_row % ants.rows) - ants.rows,
                                (d_col % ants.cols) - ants.cols
                            )))
                if 40 <= d and d <= ants.viewradius2:
                    self.vision_offsets.append(
                            ((
                                (d_row % ants.rows) - ants.rows,
                                (d_col % ants.cols) - ants.cols
                            )))
                elif d < 3:
                    self.adj_offsets.append(
                            ((
                                (d_row % ants.rows) - ants.rows,
                                (d_col % ants.cols) - ants.cols
                            )))

    def do_turn(self, ants):
        # loop through all my ants and try to give them orders
        # the ant_loc is an ant location tuple in (row, col) form
        orders = {}
        conflicts = {}
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if new_loc not in orders and new_loc not in self.impassable:
                orders[new_loc] = loc
                if not ants.unoccupied(new_loc):
                    conflicts[new_loc] = loc
                else:
                    ants.issue_order((loc, direction))
                return True
            else:
                return False

        def do_move_location(loc, dest):
            if loc == dest:
                return False
            directions = ants.direction(loc, dest)
            for direction in directions:
                if loc in available_ants and do_move_direction(loc, direction):
                    available_ants.remove(loc)
                    return True
            return False

        def get_adjacent(loc):
            l_r, l_c = loc
            return [((l_r + 1)%ants.rows, l_c), (l_r, (l_c + 1)%ants.cols), ((l_r - 1)%ants.rows, l_c), (l_r, (l_c - 1)%ants.cols)]
        def get_surrounding(loc):
            l_r, l_c = loc
            return [((l_r + 1)%ants.rows, l_c), 
                    ((l_r + 1)%ants.rows, (l_c + 1)%ants.cols),
                    (l_r, (l_c + 1)%ants.cols), 
                    ((l_r - 1)%ants.rows, (l_c + 1)%ants.cols),
                    ((l_r - 1)%ants.rows, l_c), 
                    ((l_r + 1)%ants.rows, (l_c - 1)%ants.cols),
                    (l_r, (l_c - 1)%ants.cols),
                    ((l_r - 1)%ants.rows, (l_c - 1)%ants.cols)]

        def find_path(start_loc, dest, threshold):
            # A* is based on the heuristic h = f + g,
            # where f = distance traveled so far and g = straightline distance to dest.
            # fp and gp stand for 'f prime' and 'g prime'
            if start_loc == dest:
                return start_loc
            memoization = True
            # frontier stores nodes which haven't yet been expanded.
            # nodes are in form (h, f, location, parent)
            frontier = []
            frontier_len = 0
            # visited is simply a list of all explored locations
            visited = set() 
            # initialize variables
            f = 0 
            loc = start_loc
            par = None
            # loc is the current tile being examined.
            # each loop iteration examines the frontier tile with lowest h value.
            while loc != dest and (loc, dest) not in self.stored_paths: 
                this_path_node = path_node(parent=par, location=loc)
                # expand the frontier by adding adjacent locations
                for adj_loc in get_adjacent(loc):
                    # if the location isn't passable or has already been visited, skip 
                    if adj_loc in visited or adj_loc in self.impassable:# or not ants.visible(adj_loc):
                        continue
                    else:
                        # set f' and g'
                        fp = f + 1 
                        gp = ants.distance(adj_loc, dest)
                        # add to frontier and visited
                        frontier.append(frontier_node(h_val=fp + gp, f_val=fp, location=adj_loc, parent=this_path_node))
                        frontier_len += 1
                        visited.add(adj_loc)
                # dead end. This occurs when there is no visible path to dest
                #frontier_len = len(frontier)
                # We've hit a dead end; generally shouldn't happen.
                #if frontier_len == 0:
                #    return start_loc 
                # Timeout checker.
                if frontier_len*threshold > ants.time_remaining():
                    return start_loc
                # sort frontier, so the node with highest h value is at the front
                frontier.sort(cmp = lambda x, y: y.h_val - x.h_val)
                # pop off node with the lowest h value for next iteration
                h, f, loc, par = frontier.pop()
                frontier_len -= 1
            # prev is the previous location's parent
            if (loc, dest) in self.stored_paths:
                path_dist_offset = self.path_dists[(loc, dest)] 
            else:
                path_dist_offset = 0
            final_path = deque() 
            # loop retraces back to start_loc, ends when it finds the node with no parent
            while par != None:
                # if part of the path is unknown, it could potentially be a bad path
                if loc in self.unseen:
                    memoization = False
                final_path.appendleft(loc)
                next_par, loc = par
                par = next_par
            if memoization:
                step = start_loc
                dist = len(final_path) + path_dist_offset
                for next_step in final_path:
                    self.path_dists[(step, dest)] = dist
                    self.path_dists[(dest, step)] = dist
                    dist -= 1
                    self.stored_paths[(step, dest)] = next_step
                    step = next_step
            if (start_loc, dest) in self.stored_paths:
                return self.stored_paths[(start_loc, dest)]
            else:
                return final_path[0]

        def fdistance(start_loc, dest):
            if (start_loc, dest) in self.path_dists:
                return self.path_dists[(start_loc, dest)]
            else:
                return ants.distance(start_loc, dest)

        def find_gradient(goals, value, cost, gradient_set):
            visited = set(goals)
            frontier = deque(((goal, value) for goal in goals))
            while len(frontier) > 0:
                loc, val = frontier.popleft()
                gradient_set[loc] += val
                next_val = val - cost
                if copysign(val, next_val) != val or next_val == 0:
                    continue
                for adj_loc in get_adjacent(loc): 
                    if adj_loc in visited or not ants.visible(adj_loc) or not ants.passable(adj_loc):
                        continue
                    else:
                        frontier.append((adj_loc, next_val))
                        visited.add(adj_loc)
            return

        def expand_ghost_loc(loc):
            if loc in self.explore_ghost_locs:
                self.explore_ghost_locs.remove(loc)
            row, col = loc

            adj_loc = (row + 4, col)
            if adj_loc not in self.explored and adj_loc not in self.explore_ghost_locs:
                self.explore_ghost_locs.add(adj_loc)

            adj_loc = (row - 4, col)
            if adj_loc not in self.explored and adj_loc not in self.explore_ghost_locs:
                self.explore_ghost_locs.add(adj_loc)

            adj_loc = (row, col + 4)
            if adj_loc not in self.explored and adj_loc not in self.explore_ghost_locs:
                self.explore_ghost_locs.add(adj_loc)

            adj_loc = (row, col - 4)
            if adj_loc not in self.explored and adj_loc not in self.explore_ghost_locs:
                self.explore_ghost_locs.add(adj_loc)

            return

        def expand_explore_loc(loc):
            row, col = self.explore_locs[loc]
            del self.explore_locs[loc]

            if (row + 4, col) not in self.explored:
                self.explored.add((row + 4, col))
                offset = 4
                if ants.rows - row <= 7:
                    offset_limit = ants.rows - row - 1
                else:
                    offset_limit = 7
                while offset <= offset_limit and not ants.passable((row + offset, col)): 
                    offset += 1
                if offset > offset_limit or not ants.passable((row + offset, col)):
                    expand_ghost_loc((row + 4, col))
                else:
                    self.explore_locs[(row + offset, col)] = (row + 4, col)
            if (row - 4, col) not in self.explored:
                self.explored.add((row - 4, col))
                offset = 4
                if row < 6: 
                    offset_limit = row - 1
                else:
                    offset_limit = 7
                while offset <= offset_limit and not ants.passable((row - offset, col)): 
                    offset += 1
                if offset > offset_limit or not ants.passable((row - offset, col)):
                    expand_ghost_loc((row - 4, col)) 
                else:
                    self.explore_locs[(row - offset, col)] = (row - 4, col)
            if (row, col + 4) not in self.explored:
                self.explored.add((row, col + 4))
                offset = 4
                if ants.cols - col <= 7:
                    offset_limit = ants.cols - col - 1
                else:
                    offset_limit = 7
                while offset <= offset_limit and not ants.passable((row, col + offset)): 
                    offset += 1
                if offset > offset_limit or not ants.passable((row, col + offset)):
                    expand_ghost_loc((row, col + 4))
                else:
                    self.explore_locs[(row, col + offset)] = (row, col + 4)
            if (row, col - 4) not in self.explored:
                self.explored.add((row, col - 4))
                offset = 4
                if col < 6:
                    offset_limit = col - 1 
                else:
                    offset_limit = 7
                while offset <= offset_limit and not ants.passable((row, col - offset)): 
                    offset += 1
                if offset > offset_limit or not ants.passable((row, col - offset)):
                    expand_ghost_loc((row, col - 4))
                else:
                    self.explore_locs[(row, col - offset)] = (row, col - 4)
            return

        ##
        ## end function definitions
        ##

        # Initialization

        destination = ants.destination

        
        # First turn initialization: set explore locations
        if not self.explore_loc_set:
            self.explore_locs[ants.my_hills()[0]] = ants.my_hills()[0]
            self.explore_loc_set = True

        available_ants = set(ants.my_ants())
        my_ants = ants.my_ants()
        ant_count = len(my_ants)

        enemy_ants = set((loc for loc, owner in ants.enemy_ants()))
        enemy_hills = set((loc for loc, owner in ants.enemy_hills()))
        unfriendly_gradient = defaultdict(lambda: 0) 
        friendly_gradient = defaultdict(lambda: 0) 

        self.danger.clear()
        danger = self.danger


        # Are any of our hills in danger?
        # If so, set danger locs around them.
        if ant_count > 10:
            buddysystem = True
            diagonals = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            number_of_guards = len(ants.my_hills())//14
            for h_r, h_c in ants.my_hills():
                guard_count = 0
                for diag in ((h_r + d_r, h_c + d_c) for d_r, d_c in diagonals):
                    if guard_count > number_of_guards:
                        break
                    elif diag in self.impassable:
                        continue
                    elif diag in available_ants:
                        guard_count += 1
                        orders[diag] = None
                    else:
                        guard_count += 1
                        danger[diag] = 2
        else:
            buddysystem = False

        # Update unseen
        for unseen_loc in list(self.unseen):
            if ants.visible(unseen_loc):
                self.unseen.remove(unseen_loc)
                if not ants.passable(unseen_loc):
                    self.impassable.add(unseen_loc)
                if unseen_loc in self.explore_ghost_locs:
                    if ants.passable(unseen_loc):
                        self.explore_locs[unseen_loc] = unseen_loc
                    else:
                        expand_ghost_loc(unseen_loc)

        for ant_loc in available_ants.intersection(self.explore_locs):
            expand_explore_loc(ant_loc)

        # Prevent stepping on own hill
        for hill_loc in ants.my_hills():
            if hill_loc in my_ants:
                orders[hill_loc] = None

        # update food_locs
        indexes = []
        current_food = set(ants.food())
        for food_loc in ants.food():
            self.food_locs.add(food_loc)
        for food_loc in list(self.food_locs):
            if ants.visible(food_loc) and food_loc not in current_food:
                self.food_locs.remove(food_loc)

        # update enemy hills
        for hill_loc, hill_owner in ants.enemy_hills():
            if hill_loc not in self.hills:
                self.hills.append(hill_loc)
        for hill_loc in self.hills:
            if hill_loc not in enemy_hills and ants.visible(hill_loc):
                self.hills.remove(hill_loc)
            else:
                pass

        # MDPs
        # set gradient around enemy ants
        for enemy_ant in enemy_ants:
            adj_ants = len([adj_loc for adj_loc in get_adjacent(enemy_ant) if adj_loc in enemy_ants])
            find_gradient([enemy_ant], 6 + adj_ants*6, 1 + adj_ants, unfriendly_gradient)

        hill_gradient = defaultdict(lambda: 0)
        for hill in ants.my_hills():
            if unfriendly_gradient[hill] != 0:
                find_gradient([hill], 6, 1, hill_gradient)
                find_gradient([hill], 40, 8, friendly_gradient) 

        find_gradient(enemy_hills, 64, 16, friendly_gradient)
        #find_gradient(ants.food(), 12, 2)

        # set gradient around ants in danger
        for ant_loc in my_ants: 
            if unfriendly_gradient[ant_loc] != 0:
                adj_ants = len([adj_loc for adj_loc in get_adjacent(ant_loc) if adj_loc in available_ants])
                find_gradient([ant_loc], 6 + adj_ants*6, 1 + adj_ants*2, friendly_gradient)

        # Act on the MDPs
        for ant in my_ants:
            if hill_gradient[ant] != 0:
                gradient_ratio = (unfriendly_gradient[ant] * 100) / friendly_gradient[ant] if friendly_gradient[ant] != 0 else 1
                if gradient_ratio > 55:
                    danger[ant] = 0
                    max_loc = ant
                    for adj_loc in get_adjacent(ant): 
                        if friendly_gradient[adj_loc] > friendly_gradient[max_loc] and adj_loc not in self.impassable:
                            max_loc = adj_loc
                    do_move_location(ant, max_loc)
                else:
                    max_loc = ant
                    for adj_loc in get_adjacent(ant):
                        if unfriendly_gradient[adj_loc] > unfriendly_gradient[max_loc] and adj_loc not in self.impassable:
                            max_loc = adj_loc
                    do_move_location(ant, max_loc)
            elif friendly_gradient[ant] != 0:
                gradient_ratio = (unfriendly_gradient[ant] * 100) / friendly_gradient[ant]
                if gradient_ratio > 35 or (unfriendly_gradient[ant] >= 3 and friendly_gradient[ant] <= 6):
                    danger[ant] = 2
                    min_loc = ant
                    for adj_loc in get_adjacent(ant): 
                        if unfriendly_gradient[adj_loc] < unfriendly_gradient[min_loc] and adj_loc not in self.impassable:
                            min_loc = adj_loc
                    do_move_location(ant, min_loc)
                elif gradient_ratio > 15 or unfriendly_gradient[ant] == 0:
                    danger[ant] = 2
                    max_loc = ant
                    for adj_loc in get_adjacent(ant): 
                        if friendly_gradient[adj_loc] > friendly_gradient[max_loc] and adj_loc not in self.impassable:
                            max_loc = adj_loc
                    do_move_location(ant, max_loc)
                else:
                    max_dir = 'n'
                    for dir in ('n', 'e', 's', 'w'): 
                        adj_loc = destination(ant, dir)
                        if unfriendly_gradient[adj_loc] > unfriendly_gradient[destination(ant, max_dir)] and adj_loc not in self.impassable:
                            max_dir = dir 
                    dest = destination(ant, max_dir)
                    do_move_location(ant, dest)
                    for adj_ant in get_surrounding(ant):
                        if adj_ant in available_ants:
                            dest = destination(adj_ant, max_dir)
                            do_move_location(adj_ant, dest)


        # Bookkeeping: saved move sequences from a previous turn.
        food_targets = set() 
        explore_targets = set() 
        new_bookkeeping = []
        while len(self.bookkeeping) > 0:
            type, ant_loc, target_loc = self.bookkeeping.pop()
            if ant_loc not in available_ants:
                continue
            if (ant_loc, target_loc) not in self.stored_paths:
                continue
            if type == 'food':
                if target_loc not in self.food_locs:
                    continue
                else:
                    food_targets.add(target_loc)
                    dest = self.stored_paths[(ant_loc, target_loc)]
                    do_move_location(ant_loc, dest)
                    if dest != target_loc:
                        new_bookkeeping.append(('food', dest, target_loc))
            elif type == 'hill':
                if target_loc not in self.hills:
                    continue
                else:
                    dest = self.stored_paths[(ant_loc, target_loc)]
                    do_move_location(ant_loc, dest)
                    if dest != target_loc:
                        new_bookkeeping.append(('hill', dest, target_loc))
            elif type == 'danger':
                if target_loc not in danger:
                    danger[target_loc] = 3
                elif danger[target_loc] > 2:
                    continue
                else:
                    danger[target_loc] += 1
                dest = self.stored_paths[(ant_loc, target_loc)]
                do_move_location(ant_loc, dest)
                if dest != target_loc:
                    new_bookkeeping.append(('danger', dest, target_loc))
            elif type == 'explore':
                if target_loc in explore_targets:
                    continue
                else:
                    explore_targets.add(target_loc)
                dest = self.stored_paths[(ant_loc, target_loc)]
                do_move_location(ant_loc, dest)
                if dest != target_loc:
                    new_bookkeeping.append(('explore', dest, target_loc))

        self.bookkeeping = new_bookkeeping

        # find close food
        if True:
            dists = []
            for food_loc in self.food_locs:
                if food_loc not in food_targets:
					dists.extend(((fdistance(ant_loc, food_loc), ant_loc, food_loc) for ant_loc in available_ants))
            dists.sort()
            for dist, ant_loc, food_loc in dists:
                if ant_loc not in available_ants:
                    continue
                if food_loc not in food_targets:
                    food_targets.add(food_loc)
                    dest = find_path(ant_loc, food_loc, 6)
                    do_move_location(ant_loc, dest)
                    if dest != food_loc and (dest, food_loc) in self.stored_paths:
                        self.bookkeeping.append(('food', dest, food_loc))
                        for adj_loc in get_adjacent(ant_loc):
                            if adj_loc in available_ants:
                                do_move_location(adj_loc, ant_loc)
                                self.bookkeeping.append(('food', ant_loc, food_loc))
                                

        if ants.time_remaining() > 140:
            dists = []
            for danger_loc in danger:
                if danger[danger_loc] <= 2:
                    dists.extend(((fdistance(ant_loc, danger_loc), ant_loc, danger_loc) for ant_loc in available_ants))
            dists.sort()
            for dist, ant_loc, danger_loc in dists:
                if ant_loc not in available_ants or danger[danger_loc] > 2:
                    continue
                elif ants.time_remaining() < dist*10:
                    break
                else:
                    dest = find_path(ant_loc, danger_loc, 5)
                    if do_move_location(ant_loc, dest):
                        danger[danger_loc] += 1
                        if (dest, danger_loc) in self.stored_paths:
                            self.bookkeeping.append(('danger', dest, danger_loc))
                        if buddysystem:
                            for adj_loc in get_adjacent(ant_loc): 
                                if adj_loc in available_ants:
                                    do_move_location(adj_loc, ant_loc)
                                    self.bookkeeping.append(('danger', ant_loc, danger_loc))
                                    break

        # attack hills
        if ants.time_remaining() > 80:
            dists = []
            for hill_loc in self.hills:
                dists.extend(((fdistance(ant_loc, hill_loc), ant_loc, hill_loc) for ant_loc in available_ants))
            dists.sort()
            for dist, ant_loc, hill_loc in dists:
                if ant_loc not in available_ants:
                    continue
                elif (ant_loc, hill_loc) in self.stored_paths:
                    dest = self.stored_paths[(ant_loc, hill_loc)] 
                    do_move_location(ant_loc, dest)
                    if (dest, hill_loc) in self.stored_paths:
                        self.bookkeeping.append(('hill', dest, hill_loc))
                elif ants.time_remaining() < dist*10:
                    break
                else: 
                    dest = find_path(ant_loc, hill_loc, 2)
                    do_move_location(ant_loc, dest)
                    if (dest, hill_loc) in self.stored_paths:
                        self.bookkeeping.append(('hill', dest, hill_loc))
                        if buddysystem:
                            for adj_loc in get_adjacent(ant_loc): 
                                if adj_loc in available_ants:
                                    do_move_location(adj_loc, ant_loc)
                                    self.bookkeeping.append(('hill', ant_loc, hill_loc))
                                    break
        

        # explore the map
        if ants.time_remaining() > 80:
            dists = []
            for explore_loc in self.explore_locs.iterkeys():
                for ant_loc in available_ants:
                    dist = fdistance(ant_loc, explore_loc)
                    dists.append((dist, ant_loc, explore_loc))
            dists.sort()
            for dist, ant_loc, explore_loc in dists:
                if ant_loc not in available_ants or explore_loc in explore_targets:
                    continue
                elif (ant_loc, explore_loc) in self.stored_paths:
                    do_move_location(ant_loc, self.stored_paths[(ant_loc, explore_loc)]) 
                elif ants.time_remaining() < dist*10:
                    break
                else:
                    explore_targets.add(explore_loc)
                    dest = find_path(ant_loc, explore_loc, 3)
                    do_move_location(ant_loc, dest)
                    if (dest, explore_loc) in self.stored_paths:
                        self.bookkeeping.append(('explore', dest, explore_loc))


        # For remaining ants, move in a random direction
        for ant_loc in list(available_ants):
            adj_locs = get_adjacent(ant_loc)
            shuffle(adj_locs)
            for adj_loc in adj_locs:
                if do_move_location(ant_loc, adj_loc):
                    break

        
        # Resolve move conflicts
        for c, a in conflicts.iteritems():
            if c in available_ants:
                available_ants.add(a)
            else:
                dir = ants.direction(a, c)[0]
                ants.issue_order((a, dir))




if __name__ == '__main__':
	# psyco will speed up python a little, but is not needed
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

	try:
		# if run is passed a class with a do_turn method, it will do the work
		# this is not needed, in which case you will need to write your own
		# parsing function and your own game state class
		Ants.run(MyBot())
	except KeyboardInterrupt:
		print('ctrl-c, leaving ...')
