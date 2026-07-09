from collections import deque

Coord = tuple[int, int]

PATTERN_42 = [
    (0, 0), (0, 1), (0, 2),
    (1, 2),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),

    (4, 0), (5, 0), (6, 0),
    (6, 1),
    (4, 2), (5, 2), (6, 2),
    (4, 3),
    (4, 4), (5, 4), (6, 4),
]


def _is_pattern_safe(
    width: int,
    height: int,
    pattern: set[Coord],
) -> bool:
    open_cells = {
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in pattern
    }
    if not open_cells:
        return False

    start = next(iter(open_cells))
    visited = {start}
    queue: deque[Coord] = deque([start])

    while queue:
        x, y = queue.popleft()
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            next_cell = (x + dx, y + dy)
            if next_cell in open_cells and next_cell not in visited:
                visited.add(next_cell)
                queue.append(next_cell)

    return visited == open_cells


def get_pattern_42(width: int, height: int) -> set[tuple[int, int]]:
    pattern_width = 7
    pattern_height = 5

    start_x = (width - pattern_width) // 2
    start_y = (height - pattern_height) // 2
    if (
        start_x < 0
        or start_x + pattern_width > width
        or start_y < 0
        or start_y + pattern_height > height
    ):
        return set()

    pattern = set()
    for dx, dy in PATTERN_42:
        pattern.add((start_x + dx, start_y + dy))
    if not _is_pattern_safe(width, height, pattern):
        return set()
    return pattern
