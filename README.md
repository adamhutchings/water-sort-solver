# WaterSort Solver

## Purpose
There is a popular mobile game called "WaterSortPuzzle", whose idea is that you
have vials with many disorganized colors of water in them, and your goal is to
pour water from one vial to another to get all colors together. This is made
difficult because you may not pour one color of water onto a different color, so
some careful planning is in order.

Also, my dad and I were both stuck on the same level for so long that we had to
buy an extra empty vial to get around it. So I wanted to see how to solve it.

## How to Run
Run this code with `python3 src/main.py`, where you may edit the lines in the
`main` function to reflect any level you would like. This should be
straightforward enough even for non-coders given the example.

## Technical Details
The puzzles are solved by means of A-star search. The heuristic which I use
measures the number of disparate colors which are touching, which of course
reaches zero when the puzzle is in a solved state. From practical experience
obtained by playing literal thousands of levels, the heuristic also favors the
existence of empty vials.

However, upon testing I noticed that the algorithm would often halt for long
periods of time, considering many states which are all trivially solvable. (By
this I mean that no vial has more than one color, but not all of the same color
will be together -- this is trivial in that the colors can simply be combined.)
Therefore, the algorithm halts upon seeing one of these states. Therefore, an
optimal path is not guaranteed, but it can solve the harder levels on the app
in around two seconds on my machine.

## Results

The algorithm fails on the level my dad and I were both stuck on, terminating in
around six seconds. This indicates that all possible searches were tried, so
there was in fact no solution. I feel quite vindicated now, because I was not
stuck on the level for lack of skill -- it was quite literally impossible.
