# Ball game: maze painting approximation

This folder models a ball that rolls in a straight line until a wall stops it. The ball paints every open cell it crosses. From rest, it can choose up, left, down, or right, except it cannot choose the same direction as its previous roll. Reversing is allowed. The initial position is painted before the first roll.

The goal is to estimate the fewest turns (complete rolls) needed to paint every open cell. The included solver uses bounded beam search: it expands paths by turn count and keeps the most promising states at each depth. A found solution is a valid turn-count upper bound; because the search prunes paths, it may miss a shorter solution.

## Logic

### 1. Represent the maze and a game state

The program assigns an index to every open cell. It stores the set of painted cells as a bit mask: bit `i` is `1` when cell `i` has been painted. The starting cell's bit is set before searching.

Each search state contains:

- the ball's current cell;
- the direction of its previous roll, or no direction before the first roll;
- the painted-cell bit mask;
- the sequence of directions used to reach the state.

The previous direction is part of the state because it determines which move is legal next. The painted mask is part of the state because two visits to the same cell can have different future value depending on what has already been painted.

### 2. Simulate one turn

At each turn, the solver tries each of the four directions, skipping the direction used on the previous turn. For a chosen direction, it advances cell by cell until the next cell is a wall or outside the grid. It sets the bits for every cell crossed, records the last reachable cell as the new position, and records the chosen direction as the new previous direction.

Moves that cannot travel into any cell are ignored because they paint nothing and leave the ball in place. Reversing direction is allowed as long as it differs from the previous direction.

### 3. Search in increasing turn counts

The solver starts with the initial state and generates all candidate states for turn 1, then turn 2, and so on. Therefore, the first complete cover it finds uses the fewest turns among the states that remain in the search. A complete cover is a mask with every open-cell bit set.

To keep the search manageable, each turn layer is sorted and capped at `--beam-width` states. It prefers states that have painted more distinct cells, then states that painted more new cells on their latest roll. Equivalent states (same position, previous direction, and painted mask) are deduplicated. This pruning makes the result an approximation: a promising-looking state can be discarded even if it would lead to the best full cover.

### 4. Interpret the result

- **Complete cover found:** the reported turn count and direction sequence form a valid solution. Treat the count as an upper bound on the true minimum; increasing beam width may discover a shorter one.
- **No full cover found:** the search did not find a solution within `--max-turns` and the current beam width. It does not prove that no solution exists.
- **Optimistic lower bound:** `ceil(open_cells / longest_single_roll)` is printed for a found solution. It assumes every turn can paint the longest possible roll's worth of new cells, so it is only a rough lower bound.

For the underlying mathematical model and state notation, see [`math.md`](math.md).

## Files

- `layout.txt` — sample maze (`#` wall, `.` floor, `S` starting cell). The outer edge is treated as a wall.
- `math.md` — state representation, search method, and lower bound.
- `python.py` — runnable solver.

## Run

From this directory:

```sh
python3 python.py
```

Choose another maze or adjust search limits:

```sh
python3 python.py path/to/layout.txt --beam-width 20000 --max-turns 120
```

Increasing beam width explores more states and may find a shorter cover, at the cost of memory and runtime. If the solver reports no full cover, increase the limits or check whether the maze's stopping positions and movement rules permit complete coverage.
