"""Maze generation using wall expansion algorithm."""

import random
from typing import Any

from src.mazegen.utils import get_pattern_42, DirectionMask as Direction


def gen_maze_wall_expand(width: int, height: int) -> list[list[int]]:
    """Generate maze using wall expansion method.

    Args:
        width (int): Maze width.
        height (int): Maze height.

    Returns:
        list[list[int]]: 2D grid of integer wall masks.
    """
    maze = [[0] * width for _ in range(height)]
    connected_pillars: set[tuple[int, int]] = set()

    blocked_cells = get_pattern_42(width, height)
    if blocked_cells:
        for cy, cx in blocked_cells:
            connected_pillars.update([
                (cy, cx), (cy + 1, cx), (cy, cx + 1), (cy + 1, cx + 1)
            ])
            maze[cy][cx] = 15

            if cy > 0:
                maze[cy - 1][cx] |= Direction.SOUTH
            if cy < height - 1:
                maze[cy + 1][cx] |= Direction.NORTH
            if cx > 0:
                maze[cy][cx - 1] |= Direction.EAST
            if cx < width - 1:
                maze[cy][cx + 1] |= Direction.WEST

    for w in range(width):
        maze[0][w] |= Direction.NORTH
        maze[height - 1][w] |= Direction.SOUTH
        connected_pillars.update([
            (0, w), (0, w + 1), (height, w), (height, w + 1)
        ])

    for h in range(height):
        maze[h][0] |= Direction.WEST
        maze[h][width - 1] |= Direction.EAST
        connected_pillars.update([
            (h, 0), (h + 1, 0), (h, width), (h + 1, width)
        ])

    remaining = [(h, w) for h in range(1, height) for w in range(1, width)]
    random.shuffle(remaining)

    while remaining:
        start_h, start_w = remaining.pop()

        if (start_h, start_w) in connected_pillars:
            continue

        ph, pw = start_h, start_w
        path_history = [(ph, pw)]
        temp_walls: list[tuple[int, int, int, int]] = []

        while True:
            dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            random.shuffle(dirs)

            moved = False
            for dh, dw in dirs:
                nh, nw = ph + dh, pw + dw

                if not (0 <= nh <= height and 0 <= nw <= width):
                    continue
                if (nh, nw) in path_history:
                    continue

                temp_walls.append((ph, pw, nh, nw))
                path_history.append((nh, nw))

                if (nh, nw) in connected_pillars:
                    for fh, fw, th, tw in temp_walls:
                        if fw == tw:
                            min_h = min(fh, th)
                            if fw > 0:
                                maze[min_h][fw - 1] |= Direction.EAST
                            if fw < width:
                                maze[min_h][fw] |= Direction.WEST
                        else:
                            min_w = min(fw, tw)
                            if fh > 0:
                                maze[fh - 1][min_w] |= Direction.SOUTH
                            if fh < height:
                                maze[fh][min_w] |= Direction.NORTH

                    for p in path_history:
                        connected_pillars.add(p)

                    moved = True
                    break
                else:
                    ph, pw = nh, nw
                    moved = True
                    break

            if not moved or (nh, nw) in connected_pillars:
                break

    return maze


def gen_maze_wall_expand_with_steps(
    width: int,
    height: int,
) -> tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]:
    """Generate maze using wall expansion method with step history.

    Args:
        width (int): Maze width.
        height (int): Maze height.

    Returns:
        tuple[list[list[int]],
        tuple[list[list[int]], list[list[Any]]]]: A tuple containing:
            - list[list[int]]: The final grid.
            - tuple: A tuple of (initial grid copy, list of step diffs).
    """
    maze = [[0] * width for _ in range(height)]
    connected_pillars: set[tuple[int, int]] = set()

    blocked_cells = get_pattern_42(width, height)
    if blocked_cells:
        for cy, cx in blocked_cells:
            connected_pillars.update([
                (cy, cx), (cy + 1, cx), (cy, cx + 1), (cy + 1, cx + 1)
            ])
            maze[cy][cx] = 15

            if cy > 0:
                maze[cy - 1][cx] |= Direction.SOUTH
            if cy < height - 1:
                maze[cy + 1][cx] |= Direction.NORTH
            if cx > 0:
                maze[cy][cx - 1] |= Direction.EAST
            if cx < width - 1:
                maze[cy][cx + 1] |= Direction.WEST

    for w in range(width):
        maze[0][w] |= Direction.NORTH
        maze[height - 1][w] |= Direction.SOUTH
        connected_pillars.update([
            (0, w), (0, w + 1), (height, w), (height, w + 1)
        ])

    for h in range(height):
        maze[h][0] |= Direction.WEST
        maze[h][width - 1] |= Direction.EAST
        connected_pillars.update([
            (h, 0), (h + 1, 0), (h, width), (h + 1, width)
        ])

    initial = [row[:] for row in maze]
    diffs: list[list[Any]] = []

    remaining = [(h, w) for h in range(1, height) for w in range(1, width)]
    random.shuffle(remaining)

    while remaining:
        start_h, start_w = remaining.pop()

        if (start_h, start_w) in connected_pillars:
            continue

        ph, pw = start_h, start_w
        path_history = [(ph, pw)]
        temp_walls: list[tuple[int, int, int, int]] = []

        while True:
            dirs = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            random.shuffle(dirs)

            moved = False
            for dh, dw in dirs:
                nh, nw = ph + dh, pw + dw

                if not (0 <= nh <= height and 0 <= nw <= width):
                    continue
                if (nh, nw) in path_history:
                    continue

                temp_walls.append((ph, pw, nh, nw))
                path_history.append((nh, nw))

                if (nh, nw) in connected_pillars:
                    diff = []
                    for fh, fw, th, tw in temp_walls:
                        if fw == tw:
                            min_h = min(fh, th)
                            if fw > 0:
                                maze[min_h][fw - 1] |= Direction.EAST
                                diff.append((
                                    min_h, fw - 1, maze[min_h][fw - 1]
                                ))
                            if fw < width:
                                maze[min_h][fw] |= Direction.WEST
                                diff.append((
                                    min_h, fw, maze[min_h][fw]
                                ))
                        else:
                            min_w = min(fw, tw)
                            if fh > 0:
                                maze[fh - 1][min_w] |= Direction.SOUTH
                                diff.append((
                                    fh - 1, min_w, maze[fh - 1][min_w]
                                ))
                            if fh < height:
                                maze[fh][min_w] |= Direction.NORTH
                                diff.append((
                                    fh, min_w, maze[fh][min_w]
                                ))

                    for p in path_history:
                        connected_pillars.add(p)

                    diffs.append(diff)
                    moved = True
                    break
                else:
                    ph, pw = nh, nw
                    moved = True
                    break

            if not moved or (nh, nw) in connected_pillars:
                break

    return maze, (initial, diffs)
