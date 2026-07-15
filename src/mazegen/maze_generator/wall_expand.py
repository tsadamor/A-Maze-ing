"""Maze generation using wall expansion algorithm."""

import random
from typing import Any

from mazegen.utils import DirectionMask as Direction
from mazegen.utils import get_pattern_42


Pillar = tuple[int, int]
Wall = tuple[Pillar, Pillar]


def gen_maze_wall_expand(
    width: int,
    height: int,
    entry: tuple[int, int],
) -> tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]:
    """Generate a perfect maze using randomized wall expansion.

    Existing wall components (the border and the ``42`` pattern) are tracked
    independently. Random walls are then added only when they join two
    different components. This connects every wall component without creating
    an additional wall cycle, so the remaining passages form a tree.

    Args:
        width (int): Maze width.
        height (int): Maze height.
        entry (tuple[int, int]): Entry coordinate. Kept for API consistency.

    Returns:
        tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]:
            Final maze and its initial state plus animation diffs.
    """
    del entry
    maze = [[0] * width for _ in range(height)]
    parent: dict[Pillar, Pillar] = {}
    rank: dict[Pillar, int] = {}

    def find(pillar: Pillar) -> Pillar:
        parent.setdefault(pillar, pillar)
        rank.setdefault(pillar, 0)
        if parent[pillar] != pillar:
            parent[pillar] = find(parent[pillar])
        return parent[pillar]

    def union(first: Pillar, second: Pillar) -> bool:
        first_root = find(first)
        second_root = find(second)
        if first_root == second_root:
            return False
        if rank[first_root] < rank[second_root]:
            first_root, second_root = second_root, first_root
        parent[second_root] = first_root
        if rank[first_root] == rank[second_root]:
            rank[first_root] += 1
        return True

    def place_wall(
        first: Pillar,
        second: Pillar,
    ) -> list[tuple[int, int, int]]:
        first_h, first_w = first
        second_h, second_w = second
        diff: list[tuple[int, int, int]] = []

        if first_w == second_w:
            row = min(first_h, second_h)
            if first_w > 0:
                maze[row][first_w - 1] |= Direction.EAST
                diff.append((row, first_w - 1, maze[row][first_w - 1]))
            if first_w < width:
                maze[row][first_w] |= Direction.WEST
                diff.append((row, first_w, maze[row][first_w]))
        else:
            col = min(first_w, second_w)
            if first_h > 0:
                maze[first_h - 1][col] |= Direction.SOUTH
                diff.append((first_h - 1, col, maze[first_h - 1][col]))
            if first_h < height:
                maze[first_h][col] |= Direction.NORTH
                diff.append((first_h, col, maze[first_h][col]))
        return diff

    existing_walls: list[Wall] = []

    for col in range(width):
        existing_walls.append(((0, col), (0, col + 1)))
        existing_walls.append(((height, col), (height, col + 1)))
    for row in range(height):
        existing_walls.append(((row, 0), (row + 1, 0)))
        existing_walls.append(((row, width), (row + 1, width)))

    blocked_cells = get_pattern_42(width, height)
    for row, col in blocked_cells:
        maze[row][col] = 15
        existing_walls.extend([
            ((row, col), (row, col + 1)),
            ((row, col + 1), (row + 1, col + 1)),
            ((row + 1, col), (row + 1, col + 1)),
            ((row, col), (row + 1, col)),
        ])

    for first, second in existing_walls:
        union(first, second)
        place_wall(first, second)

    initial = [row[:] for row in maze]
    diffs: list[list[Any]] = []
    candidates: list[Wall] = []

    for row in range(height + 1):
        for col in range(width):
            candidates.append(((row, col), (row, col + 1)))
    for row in range(height):
        for col in range(width + 1):
            candidates.append(((row, col), (row + 1, col)))
    random.shuffle(candidates)

    for first, second in candidates:
        if union(first, second):
            diff = place_wall(first, second)
            if diff:
                diffs.append(diff)

    return maze, (initial, diffs)
