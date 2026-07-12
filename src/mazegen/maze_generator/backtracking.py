"""Backtracking DFS maze generation algorithm."""

import random
from typing import Any

from mazegen.utils import DirectionMask, get_pattern_42


def generate_maze_dfs(
    width: int,
    height: int,
    entry: tuple[int, int],
) -> tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]:
    """Generate a perfect maze using DFS and return step history for animation.

    Args:
        width (int): Number of columns.
        height (int): Number of rows.
        entry (tuple[int, int]): Entry coordinate as (row, col).

    Returns:
        tuple[list[list[int]],
        tuple[list[list[int]], list[list[Any]]]]: A tuple containing:
            - list[list[int]]: The final grid.
            - tuple: A tuple of (initial grid copy, list of step diffs).
    """
    ALL_WALLS = (
        DirectionMask.NORTH
        | DirectionMask.EAST
        | DirectionMask.SOUTH
        | DirectionMask.WEST
    )
    grid = [[ALL_WALLS for _ in range(width)] for _ in range(height)]
    directions = [
        (DirectionMask.NORTH, DirectionMask.SOUTH, -1, 0),
        (DirectionMask.EAST, DirectionMask.WEST, 0, 1),
        (DirectionMask.SOUTH, DirectionMask.NORTH, 1, 0),
        (DirectionMask.WEST, DirectionMask.EAST, 0, -1),
    ]
    stack = [entry]
    visited = {entry}
    blocked_area = get_pattern_42(width, height)

    if blocked_area:
        visited.update(blocked_area)

    initial = [row[:] for row in grid]
    diffs: list[list[Any]] = []

    while stack:
        row, col = stack[-1]
        valid_neighbors = []

        for mask, opposite_mask, delta_row, delta_col in directions:
            next_row = row + delta_row
            next_col = col + delta_col
            if (
                0 <= next_row < height
                and 0 <= next_col < width
                and (next_row, next_col) not in visited
            ):
                valid_neighbors.append(
                    (mask, opposite_mask, next_row, next_col)
                )
        if valid_neighbors:
            chosen = random.choice(valid_neighbors)
        else:
            stack.pop()
            continue

        mask, opposite_mask, next_row, next_col = chosen
        grid[row][col] ^= mask
        grid[next_row][next_col] ^= opposite_mask

        stack.append((next_row, next_col))
        visited.add((next_row, next_col))

        diffs.append([
            (row, col, grid[row][col]),
            (next_row, next_col, grid[next_row][next_col]),
        ])

    return grid, (initial, diffs)
