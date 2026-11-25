# Ball game: maze painting approximation

This folder models a ball that rolls in a straight line until a wall stops it. The ball paints every open cell it crosses. From rest, it can choose up, left, down, or right, except it cannot choose the same direction as its previous roll. Reversing is allowed. The initial position is painted before the first roll.

The goal is to estimate the fewest turns (complete rolls) needed to paint every open cell. The included solver uses bounded beam search: it expands paths by turn count and keeps the most promising states at each depth. A found solution is a valid turn-count upper bound and is minimum within the explored beam, though beam pruning means global optimality is not guaranteed.

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
