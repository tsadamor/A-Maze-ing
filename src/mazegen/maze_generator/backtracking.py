"""Backtracking DFS maze generation algorithm."""

import random
from typing import Any

from .utils import get_pattern_42


def generate_maze_dfs(
    width: int,
    height: int,
    entry: tuple[int, int],
) -> list[list[int]]:
    """Generate a perfect maze using randomized depth-first search.

    Args:
        width (int): Number of columns.
        height (int): Number of rows.
        entry (tuple[int, int]): Entry coordinate as (row, col).

    Returns:
        list[list[int]]: 2D list of integer wall masks.
    """
    grid = [[15 for _ in range(width)] for _ in range(height)]
    directions = [(0, -1, 0), (1, 0, 1), (2, 1, 0), (3, 0, -1)]
    stack = [entry]
    visited = {entry}
    blocked_area = get_pattern_42(width, height)

    if blocked_area:
        visited.update(blocked_area)

    while stack:
        row, col = stack[-1]
        valid_neighbors = []

        for bit_pos, dr, dc in directions:
            nr = row + dr
            nc = col + dc
            if (
                0 <= nr < height
                and 0 <= nc < width
                and (nr, nc) not in visited
            ):
                valid_neighbors.append((bit_pos, nr, nc))
        if valid_neighbors:
            chosen = random.choice(valid_neighbors)
        else:
            stack.pop()
            continue

        bit_pos, nr, nc = chosen
        opposite_bit_pos = (bit_pos + 2) % 4
        grid[row][col] ^= 1 << bit_pos
        grid[nr][nc] ^= 1 << opposite_bit_pos

        stack.append((nr, nc))
        visited.add((nr, nc))

    return grid


def generate_maze_dfs_with_steps(
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
    grid = [[15 for _ in range(width)] for _ in range(height)]
    directions = [(0, -1, 0), (1, 0, 1), (2, 1, 0), (3, 0, -1)]
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

        for bit_pos, dr, dc in directions:
            nr = row + dr
            nc = col + dc
            if (
                0 <= nr < height
                and 0 <= nc < width
                and (nr, nc) not in visited
            ):
                valid_neighbors.append((bit_pos, nr, nc))
        if valid_neighbors:
            chosen = random.choice(valid_neighbors)
        else:
            stack.pop()
            continue

        bit_pos, nr, nc = chosen
        opposite_bit_pos = (bit_pos + 2) % 4
        grid[row][col] ^= 1 << bit_pos
        grid[nr][nc] ^= 1 << opposite_bit_pos

        stack.append((nr, nc))
        visited.add((nr, nc))

        diffs.append([
            (row, col, grid[row][col]),
            (nr, nc, grid[nr][nc]),
        ])

    return grid, (initial, diffs)
