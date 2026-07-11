"""Braided (Pac-Man style non-perfect) maze generation algorithm."""

import random
from typing import Any

from .backtracking import generate_maze_dfs, generate_maze_dfs_with_steps
from .utils import get_pattern_42, DirectionMask


def _count_open_walls(mask: int) -> int:
    """Count number of open walls (0 bits) in a cell mask.

    Args:
        mask (int): Cell wall mask representation.

    Returns:
        int: The number of open walls (0-bits) in the mask.
    """
    return sum(
        1 for m in (
            DirectionMask.NORTH,
            DirectionMask.EAST,
            DirectionMask.SOUTH,
            DirectionMask.WEST
        ) if (mask & m) == 0
    )


def generate_maze_pacman(
    width: int,
    height: int,
    entry: tuple[int, int],
) -> list[list[int]]:
    """Generate a playable Pac-Man style board (PERFECT=False).

    Ensures full connectivity, open corridors at corners/center, multiple
    routes (loops), and eliminates dead-ends outside the '42' pattern.

    Args:
        width (int): Number of columns.
        height (int): Number of rows.
        entry (tuple[int, int]): Entry coordinate as (row, col).

    Returns:
        list[list[int]]: 2D list of integer wall masks representing the
            braided maze.
    """
    grid = generate_maze_dfs(width, height, entry)
    blocked_area = get_pattern_42(width, height)
    directions = [
        (DirectionMask.NORTH, DirectionMask.SOUTH, -1, 0),
        (DirectionMask.EAST, DirectionMask.WEST, 0, 1),
        (DirectionMask.SOUTH, DirectionMask.NORTH, 1, 0),
        (DirectionMask.WEST, DirectionMask.EAST, 0, -1),
    ]

    while True:
        dead_ends = []
        for r in range(height):
            for c in range(width):
                if (r, c) in blocked_area:
                    continue
                if _count_open_walls(grid[r][c]) == 1:
                    dead_ends.append((r, c))

        removed_any = False
        random.shuffle(dead_ends)
        for r, c in dead_ends:
            if _count_open_walls(grid[r][c]) != 1:
                continue
            candidates = []
            dead_end_candidates = []

            for mask, opposite_mask, delta_row, delta_col in directions:
                next_row, next_col = r + delta_row, c + delta_col
                if not (0 <= next_row < height and 0 <= next_col < width):
                    continue
                if (next_row, next_col) in blocked_area:
                    continue
                if grid[r][c] & mask:
                    candidates.append((
                        mask, opposite_mask, next_row, next_col
                    ))
                    if _count_open_walls(grid[next_row][next_col]) == 1:
                        dead_end_candidates.append((
                            mask, opposite_mask, next_row, next_col
                        ))

            chosen = None
            if dead_end_candidates:
                chosen = random.choice(dead_end_candidates)
            elif candidates:
                chosen = random.choice(candidates)

            if chosen is not None:
                mask, opposite_mask, next_row, next_col = chosen
                grid[r][c] &= ~mask
                grid[next_row][next_col] &= ~opposite_mask
                removed_any = True

        if not removed_any:
            break

    return grid


def generate_maze_pacman_with_steps(
    width: int,
    height: int,
    entry: tuple[int, int],
) -> tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]:
    """Generate a playable Pac-Man style board with animation step history.

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
    grid, (initial, diffs) = generate_maze_dfs_with_steps(width, height, entry)
    blocked_area = get_pattern_42(width, height)
    directions = [
        (DirectionMask.NORTH, DirectionMask.SOUTH, -1, 0),
        (DirectionMask.EAST, DirectionMask.WEST, 0, 1),
        (DirectionMask.SOUTH, DirectionMask.NORTH, 1, 0),
        (DirectionMask.WEST, DirectionMask.EAST, 0, -1),
    ]

    while True:
        dead_ends = []
        for r in range(height):
            for c in range(width):
                if (r, c) in blocked_area:
                    continue
                if _count_open_walls(grid[r][c]) == 1:
                    dead_ends.append((r, c))

        removed_any = False
        random.shuffle(dead_ends)
        for r, c in dead_ends:
            if _count_open_walls(grid[r][c]) != 1:
                continue
            candidates = []
            dead_end_candidates = []

            for mask, opposite_mask, delta_row, delta_col in directions:
                next_row, next_col = r + delta_row, c + delta_col
                if not (0 <= next_row < height and 0 <= next_col < width):
                    continue
                if (next_row, next_col) in blocked_area:
                    continue
                if grid[r][c] & mask:
                    candidates.append((
                        mask, opposite_mask, next_row, next_col
                    ))
                    if _count_open_walls(grid[next_row][next_col]) == 1:
                        dead_end_candidates.append((
                            mask, opposite_mask, next_row, next_col
                        ))

            chosen = None
            if dead_end_candidates:
                chosen = random.choice(dead_end_candidates)
            elif candidates:
                chosen = random.choice(candidates)

            if chosen is not None:
                mask, opposite_mask, next_row, next_col = chosen
                grid[r][c] &= ~mask
                grid[next_row][next_col] &= ~opposite_mask
                diffs.append([
                    (r, c, grid[r][c]),
                    (next_row, next_col, grid[next_row][next_col]),
                ])
                removed_any = True

        if not removed_any:
            break

    return grid, (initial, diffs)
