"""Braided (Pac-Man style non-perfect) maze generation algorithm."""

import random
from typing import Any

from .backtracking import generate_maze_dfs, generate_maze_dfs_with_steps
from .utils import get_pattern_42


def _count_open_walls(mask: int) -> int:
    """Count number of open walls (0 bits) in a cell mask.

    Args:
        mask (int): Cell wall mask representation.

    Returns:
        int: The number of open walls (0-bits) in the mask.
    """
    return sum(1 for b in range(4) if (mask & (1 << b)) == 0)


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
    directions = [(0, -1, 0), (1, 0, 1), (2, 1, 0), (3, 0, -1)]

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

            for bit_pos, dr, dc in directions:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < height and 0 <= nc < width):
                    continue
                if (nr, nc) in blocked_area:
                    continue
                if grid[r][c] & (1 << bit_pos):
                    candidates.append((bit_pos, nr, nc))
                    if _count_open_walls(grid[nr][nc]) == 1:
                        dead_end_candidates.append((bit_pos, nr, nc))

            chosen = None
            if dead_end_candidates:
                chosen = random.choice(dead_end_candidates)
            elif candidates:
                chosen = random.choice(candidates)

            if chosen is not None:
                bit_pos, nr, nc = chosen
                opp_bit = (bit_pos + 2) % 4
                grid[r][c] &= ~(1 << bit_pos)
                grid[nr][nc] &= ~(1 << opp_bit)
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
    directions = [(0, -1, 0), (1, 0, 1), (2, 1, 0), (3, 0, -1)]

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

            for bit_pos, dr, dc in directions:
                nr, nc = r + dr, c + dc
                if not (0 <= nr < height and 0 <= nc < width):
                    continue
                if (nr, nc) in blocked_area:
                    continue
                if grid[r][c] & (1 << bit_pos):
                    candidates.append((bit_pos, nr, nc))
                    if _count_open_walls(grid[nr][nc]) == 1:
                        dead_end_candidates.append((bit_pos, nr, nc))

            chosen = None
            if dead_end_candidates:
                chosen = random.choice(dead_end_candidates)
            elif candidates:
                chosen = random.choice(candidates)

            if chosen is not None:
                bit_pos, nr, nc = chosen
                opp_bit = (bit_pos + 2) % 4
                grid[r][c] &= ~(1 << bit_pos)
                grid[nr][nc] &= ~(1 << opp_bit)
                diffs.append([
                    (r, c, grid[r][c]),
                    (nr, nc, grid[nr][nc]),
                ])
                removed_any = True

        if not removed_any:
            break

    return grid, (initial, diffs)
