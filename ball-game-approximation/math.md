# State model and search

## Maze model

The maze is a finite orthogonal grid. `#` is a wall, `.` is open floor, and `S` is the ball's starting cell (also open floor). The outside edge acts as a wall. A roll follows one cardinal direction until the next step would enter a wall or leave the grid. Every open cell traversed during a roll is painted. The ball may not choose the same direction as its immediately previous roll; it may reverse direction. The first roll has no restriction.

One turn means one complete roll from rest to rest. The objective is to paint every open cell using as few turns as possible.

## Search state

For a maze with `N` open cells, encode the painted set as an `N`-bit integer. A search state is

`(position, previous_direction, painted_mask)`.

For each allowed direction, simulate a complete roll, add all traversed cells to the mask, and make the stopping cell the new position. A state with every bit set is a solution. Breadth-first search over these states would find an exact minimum, but the number of possible masks is exponential (`2^N`).

## Bounded beam approximation

The Python program searches one turn-count layer at a time, so any returned path is a valid upper bound on the minimum. At each depth it retains at most `beam_width` states, ranking them by:

1. most painted cells;
2. most newly painted cells on the latest roll;
3. lower estimated remaining travel, preferring states whose next rolls can reach unpainted cells.

Equivalent states are deduplicated. If the beam finds a complete cover at depth `k`, then `k` turns is the minimum within the explored beam; pruning means it is not guaranteed to be the global minimum. If it reaches the depth limit without covering the maze, no complete solution was found under those search settings.

The optimistic lower bound `ceil(unpainted_cells / longest_roll)` is also printed. It is useful as a sanity check, but it ignores path connectivity and can be far below the true minimum.
