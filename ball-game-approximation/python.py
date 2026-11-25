#!/usr/bin/env python3
"""Bounded beam search for the minimum rolls needed to paint a maze."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

DIRECTIONS = ((-1, 0, "U"), (0, -1, "L"), (1, 0, "D"), (0, 1, "R"))


@dataclass(frozen=True)
class State:
    pos: tuple[int, int]
    previous: int | None
    painted: int
    path: tuple[int, ...]
    new_cells: int


def read_maze(path: Path):
    rows = [line.rstrip("\n") for line in path.read_text().splitlines() if line.strip()]
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Maze must be a non-empty rectangular grid.")
    cells = {}
    start = None
    for r, row in enumerate(rows):
        for c, char in enumerate(row):
            if char in ".S":
                cells[(r, c)] = len(cells)
                if char == "S":
                    if start is not None:
                        raise ValueError("Maze must contain exactly one S.")
                    start = (r, c)
            elif char != "#":
                raise ValueError(f"Unsupported maze character: {char!r}")
    if start is None:
        raise ValueError("Maze must contain one S start cell.")
    return rows, cells, start


def roll(rows, cells, pos, direction):
    dr, dc, _ = DIRECTIONS[direction]
    r, c = pos
    traversed = []
    while (r + dr, c + dc) in cells:
        r, c = r + dr, c + dc
        traversed.append(cells[(r, c)])
    return (r, c), traversed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("layout", nargs="?", type=Path, default=Path(__file__).with_name("layout.txt"))
    parser.add_argument("--beam-width", type=int, default=10000)
    parser.add_argument("--max-turns", type=int, default=100)
    args = parser.parse_args()
    if args.beam_width < 1 or args.max_turns < 1:
        parser.error("beam-width and max-turns must be positive")

    rows, cells, start = read_maze(args.layout)
    goal = (1 << len(cells)) - 1
    start_bit = 1 << cells[start]
    longest_roll = max((len(roll(rows, cells, pos, d)[1]) for pos in cells for d in range(4)), default=1)
    beam = [State(start, None, start_bit, (), 1)]
    seen = {(start, None, start_bit)}

    for depth in range(1, args.max_turns + 1):
        candidates = {}
        for state in beam:
            for direction in range(4):
                if direction == state.previous:
                    continue
                destination, traversed = roll(rows, cells, state.pos, direction)
                mask = state.painted
                added = 0
                for index in traversed:
                    bit = 1 << index
                    if not mask & bit:
                        added += 1
                    mask |= bit
                # A direction always runs to the last reachable cell. Avoid no-op loops.
                key = (destination, direction, mask)
                if not traversed or key in seen:
                    continue
                next_state = State(destination, direction, mask, state.path + (direction,), added)
                if mask == goal:
                    print_result(next_state, len(cells), longest_roll)
                    return
                candidates[key] = next_state

        if not candidates:
            break
        states = list(candidates.values())
        states.sort(key=lambda s: (s.painted.bit_count(), s.new_cells,
                                  -((len(cells) - s.painted.bit_count() + longest_roll - 1) // longest_roll)),
                    reverse=True)
        beam = states[:args.beam_width]
        seen.update((s.pos, s.previous, s.painted) for s in beam)

    best = max(beam, key=lambda s: s.painted.bit_count())
    print(f"No full cover found within {args.max_turns} turns (beam width {args.beam_width}).")
    print(f"Best coverage: {best.painted.bit_count()}/{len(cells)} cells in {len(best.path)} turns.")
    print("Best path:", " ".join(DIRECTIONS[d][2] for d in best.path) or "(none)")


def print_result(state, total, longest_roll):
    turns = len(state.path)
    print(f"Complete cover found in {turns} turns (bounded beam search).")
    print("Path:", " ".join(DIRECTIONS[d][2] for d in state.path))
    print(f"Painted: {total}/{total} cells")
    print(f"Optimistic lower bound: {(total + longest_roll - 1) // longest_roll} turns")


if __name__ == "__main__":
    main()
