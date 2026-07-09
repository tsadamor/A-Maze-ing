import random

from maze_generator.utils import get_pattern_42

NORTH = 1 << 0
EAST = 1 << 1
SOUTH = 1 << 2
WEST = 1 << 3

DIRECTIONS = [
    (-1, 0, NORTH, SOUTH),
    (0, 1, EAST, WEST),
    (1, 0, SOUTH, NORTH),
    (0, -1, WEST, EAST),
]


def _blocked_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return closed '42' pattern cells as (row, column) coordinates."""
    return {(y, x) for x, y in get_pattern_42(width, height)}


def _is_corridor(
    maze: list[list[int]],
    y: int,
    x: int,
    blocked_cells: set[tuple[int, int]],
) -> bool:
    """Return whether a cell should be treated as a walkable corridor."""
    return (y, x) not in blocked_cells and maze[y][x] != 15


def _degree(
    maze: list[list[int]],
    width: int,
    height: int,
    y: int,
    x: int,
    blocked_cells: set[tuple[int, int]],
) -> int:
    """Count open walkable neighbours for one cell."""
    count = 0
    for dy, dx, wall, _ in DIRECTIONS:
        ny = y + dy
        nx = x + dx
        if not (0 <= ny < height and 0 <= nx < width):
            continue
        if not _is_corridor(maze, ny, nx, blocked_cells):
            continue
        if maze[y][x] & wall:
            continue
        count += 1
    return count


def _open_wall(
    maze: list[list[int]],
    y: int,
    x: int,
    ny: int,
    nx: int,
    wall: int,
    opposite_wall: int,
) -> list[tuple[int, int, int]]:
    """Open a shared wall and return the changed cells for animation."""
    maze[y][x] &= ~wall
    maze[ny][nx] &= ~opposite_wall
    return [(y, x, maze[y][x]), (ny, nx, maze[ny][nx])]


def _seal_cell(
    maze: list[list[int]],
    width: int,
    height: int,
    y: int,
    x: int,
) -> list[tuple[int, int, int]]:
    """Turn one unavoidable pocket into a closed blocker."""
    diff = []
    maze[y][x] = NORTH | EAST | SOUTH | WEST
    diff.append((y, x, maze[y][x]))
    for dy, dx, _, opposite_wall in DIRECTIONS:
        ny = y + dy
        nx = x + dx
        if 0 <= ny < height and 0 <= nx < width:
            maze[ny][nx] |= opposite_wall
            diff.append((ny, nx, maze[ny][nx]))
    return diff


def _closed_neighbours(
    maze: list[list[int]],
    width: int,
    height: int,
    y: int,
    x: int,
    blocked_cells: set[tuple[int, int]],
) -> list[tuple[int, int, int, int]]:
    """Return walkable neighbours separated from the cell by a wall."""
    candidates = []
    for dy, dx, wall, opposite_wall in DIRECTIONS:
        ny = y + dy
        nx = x + dx
        if not (0 <= ny < height and 0 <= nx < width):
            continue
        if not _is_corridor(maze, ny, nx, blocked_cells):
            continue
        if maze[y][x] & wall:
            candidates.append((ny, nx, wall, opposite_wall))
    return candidates


def _find_dead_ends(
    maze: list[list[int]],
    width: int,
    height: int,
    blocked_cells: set[tuple[int, int]],
) -> list[tuple[int, int]]:
    """Return all walkable cells with only one open neighbour."""
    dead_ends = []
    for y in range(height):
        for x in range(width):
            if not _is_corridor(maze, y, x, blocked_cells):
                continue
            if _degree(maze, width, height, y, x, blocked_cells) == 1:
                dead_ends.append((y, x))
    return dead_ends


def _touches_blocked_cell(
    y: int,
    x: int,
    blocked_cells: set[tuple[int, int]],
) -> bool:
    """Return whether a cell is directly beside the solid '42' pattern."""
    for dy, dx, _, _ in DIRECTIONS:
        if (y + dy, x + dx) in blocked_cells:
            return True
    return False


def braid_maze(
    maze: list[list[int]],
    width: int,
    height: int,
    protected_cells: set[tuple[int, int]] | None = None,
) -> tuple[list[list[int]], list[list[tuple[int, int, int]]]]:
    """Remove dead-ends from a perfect maze by adding internal passages.

    The operation only removes walls between existing corridor cells, so the
    maze stays connected and gains loops. Closed cells used for the visible
    "42" are preserved as solid blockers.
    """
    blocked_cells = _blocked_cells(width, height)
    if protected_cells is None:
        protected_cells = set()
    diffs: list[list[tuple[int, int, int]]] = []
    opened_walls = 0

    while True:
        dead_ends = _find_dead_ends(maze, width, height, blocked_cells)
        if not dead_ends:
            break
        random.shuffle(dead_ends)
        changed = False
        for y, x in dead_ends:
            if _degree(maze, width, height, y, x, blocked_cells) != 1:
                continue
            candidates = _closed_neighbours(
                maze, width, height, y, x, blocked_cells
            )
            if not candidates:
                if _touches_blocked_cell(y, x, blocked_cells):
                    continue
                if (y, x) not in protected_cells:
                    diffs.append(_seal_cell(maze, width, height, y, x))
                    blocked_cells.add((y, x))
                    changed = True
                continue
            candidates.sort(
                key=lambda item: _degree(
                    maze, width, height, item[0], item[1], blocked_cells
                ),
                reverse=True,
            )
            ny, nx, wall, opposite_wall = candidates[0]
            diffs.append(_open_wall(maze, y, x, ny, nx, wall, opposite_wall))
            opened_walls += 1
            changed = True
        if not changed:
            break

    while opened_walls < 2:
        extra_candidates: list[tuple[int, int, int, int, int, int]] = []
        for y in range(height):
            for x in range(width):
                if not _is_corridor(maze, y, x, blocked_cells):
                    continue
                extra_candidates.extend(
                    (y, x, ny, nx, wall, opposite_wall)
                    for ny, nx, wall, opposite_wall in _closed_neighbours(
                        maze, width, height, y, x, blocked_cells
                    )
                    if (y, x) < (ny, nx)
                )
        if not extra_candidates:
            break
        y, x, ny, nx, wall, opposite_wall = random.choice(extra_candidates)
        diffs.append(_open_wall(maze, y, x, ny, nx, wall, opposite_wall))
        opened_walls += 1

    return maze, diffs
