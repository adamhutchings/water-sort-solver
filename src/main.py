from heapq import heappop, heappush
import sys
from typing import Dict, List

# All colors used in the game.
DRY_GREEN = 1
GRAY = 2
LUSH_GREEN = 3
PINK = 4
BROWN = 5
LIGHT_BLUE = 6
LIME_GREEN = 7
DARK_BLUE = 8
YELLOW = 9
PURPLE = 10
RED = 11
BLUE_BLUE = 12

class WaterSortState:

    vials: List[List[int]]
    max_vials: int
    max_height: int
    # Store the last pour made for convenience in the output.
    last_pour_src: int
    last_pour_dest: int

    def __init__(self, vial_count: int, max_height: int):
        self.vials = [[]] * vial_count
        self.max_vials = vial_count
        self.max_height = max_height

    def set_vial_at_idx(self, vial: List[int], idx: int):
        self.vials[idx] = vial.copy()

    def add_vial(self, vial: List[int]):
        if len(vial) > self.max_height:
            print("Error: tried to add too large a vial.")
            return
        first_empty_index = 0
        for i in range(self.max_vials):
            if self.vials[i] == []:
                first_empty_index = i
                break
        self.set_vial_at_idx(vial, first_empty_index)

    # This says whether a pour from vial i to vial j is possible. This check is
    # done to avoid unnecessary copying.
    def is_pour_possible(self, i: int, j: int) -> bool:
        # Just to check.
        if i == j:
            return False
        if self.vials[i] == []:
            return False
        if self.vials[j] == []:
            return True
        if self.vials[j][-1] == self.vials[i][-1]:
            # If the colors match, we need to make sure that there is room for
            # a pour to take place.
            if len(self.vials[j]) < self.max_height:
                return True
        return False
    
    # Makes a copy of the current state.
    def copy(self):
        ret = WaterSortState(self.max_vials, self.max_height)
        for i in range(self.max_vials):
            ret.set_vial_at_idx(self.vials[i], i)
        return ret
    
    # Actually performs a pour from one vial to another.
    def do_pour(self, i: int, j: int):
        ret: WaterSortState = self.copy()
        starting_color: int = ret.vials[i][-1]
        while ret.vials[i] != [] and ret.vials[i][-1] == starting_color and len(ret.vials[j]) < ret.max_height:
            ret.vials[j].append(ret.vials[i].pop())
        ret.last_pour_src = i
        ret.last_pour_dest = j
        return ret
    
    # Check if two states are equivalent.
    def __eq__(self, other) -> bool:
        self_vials = self.vials.copy()
        other_vials = other.vials.copy()
        self_vials.sort()
        other_vials.sort()
        return self_vials == other_vials
    
    def all_possible_children(self) -> List:
        children = []
        for i in range(self.max_vials):
            for j in range(self.max_vials):
                if self.is_pour_possible(i, j):
                    new_state = self.do_pour(i, j)
                    if new_state != self and new_state not in children:
                        children.append(new_state)
        return children
    
    def heuristic(self):
        # We'll go through and count the number of swaps to different colors
        # we see. This is admissible because each pour can only decrease this
        # by one, if at all.
        # We also need to penalize having vials that are not full, as well as
        # not having empty vials.
        swaps = 0
        unfull = 0
        empties = 0
        for vial in self.vials:
            for i in range(1, len(vial)):
                if vial[i] != vial[i - 1]:
                    swaps += 1
                if len(vial) < self.max_height:
                    unfull += 1
                if vial == []:
                    empties += 1
        cost = swaps + unfull
        cost *= (2/3) ** empties
        return cost
    
    def is_solved(self):
        return self.heuristic() == 0
    
    def __hash__(self) -> int:
        # Concatenate all lists together and hash that.
        megalist = []
        vial_copy = self.vials.copy()
        vial_copy.sort()
        for vial in vial_copy:
            megalist.extend(vial)
        return tuple(megalist).__hash__()
    
def get_moves(state: WaterSortState, prevs: Dict[WaterSortState, WaterSortState]) -> List[tuple[int]]:
    moves = []
    while state is not None:
        moves.append((state.last_pour_src, state.last_pour_dest))
        state = prevs[state]
    moves.reverse()
    return moves[1:]
    
# Returns a list of all states found so far
def find_solution_path(start: WaterSortState) -> List[tuple[int]]:
    nodes: List[tuple(int, WaterSortState)] = []
    # Maps each node to its predecessor.
    prevs: Dict[WaterSortState, WaterSortState] = {}
    # Storing all nodes that exist so we can check for them in O(1).
    nodes_seen: Dict[WaterSortState, True] = {}
    # Also storing cost taken to get to each node.
    node_costs: Dict[WaterSortState, int] = {}
    heappush(nodes, (start.heuristic(), start))
    start.last_pour_dest = -1
    start.last_pour_src = -1
    prevs[start] = None
    node_costs[start] = 0
    num_nodes_considered = 0
    while True:
        if nodes == []:
            print("Failed to find a solution! This level is impossible!")
            sys.exit()
        node = heappop(nodes)
        nodes_seen[node] = True
        state: WaterSortState = node[1]
        if state.is_solved():
            return get_moves(state, prevs)
        new_nodes: List[WaterSortState] = state.all_possible_children()
        for nnode in new_nodes:
            if nnode not in nodes_seen:
                num_nodes_considered += 1
                nodes_seen[nnode] = True
                prevs[nnode] = state
                node_costs[nnode] = node_costs[state] + 1
                actual_cost = node_costs[nnode] + nnode.heuristic()
                # Unfortunately, if there is a tie the program doesn't like it.
                # So we break the tie by considering earlier nodes first.
                actual_cost += num_nodes_considered / 1000000
                heappush(nodes, (actual_cost, nnode))

def show_moves(moves: List[tuple[int]]):
    for move in moves:
        print(f"Pour vial {move[0] + 1} into vial {move[1] + 1}.")

def main():

    # 14 total vials, 4 colors to a vial at most.
    puzzle: WaterSortState = WaterSortState(14, 4)

    # IT FAILS HERE. I KNEW THIS LEVEL WAS IMPOSSIBLE!!!
    puzzle.add_vial([LUSH_GREEN, YELLOW, PINK, LIGHT_BLUE])
    puzzle.add_vial([PURPLE, YELLOW, PINK, LIME_GREEN])
    puzzle.add_vial([PURPLE, RED, LIGHT_BLUE, LUSH_GREEN])
    puzzle.add_vial([PURPLE, BLUE_BLUE, GRAY, PINK])
    puzzle.add_vial([DARK_BLUE, YELLOW, YELLOW, DRY_GREEN])
    puzzle.add_vial([DARK_BLUE, BLUE_BLUE, LIME_GREEN, BLUE_BLUE])
    puzzle.add_vial([DRY_GREEN, LIGHT_BLUE, BLUE_BLUE, LUSH_GREEN])
    puzzle.add_vial([BROWN, PURPLE, GRAY, BROWN])
    puzzle.add_vial([BROWN, RED, RED, GRAY])
    puzzle.add_vial([DARK_BLUE, BROWN, PINK, DRY_GREEN])
    puzzle.add_vial([LIME_GREEN, RED, LIGHT_BLUE, GRAY])
    puzzle.add_vial([LIME_GREEN, LUSH_GREEN, DRY_GREEN, DARK_BLUE])

    moves = find_solution_path(puzzle)
    show_moves(moves)

if __name__ == '__main__':
    main()
