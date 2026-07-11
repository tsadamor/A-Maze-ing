"""42 pattern generator for A-Maze-ing project."""

# PATTERN_42 stores (col_offset, row_offset) for the 7x5 block "42" pattern
PATTERN_42 = [
    # Digit 4
    (0, 0), (0, 1), (0, 2),
    (1, 2),
    (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),

    # Digit 2
    (4, 0), (5, 0), (6, 0),
    (6, 1),
    (4, 2), (5, 2), (6, 2),
    (4, 3),
    (4, 4), (5, 4), (6, 4),
]


def get_pattern_42(width: int, height: int) -> set[tuple[int, int]]:
    """Get grid coordinates (row, col) for the visible '42' pattern.

    Args:
        width (int): Number of columns in the maze.
        height (int): Number of rows in the maze.

    Returns:
        set[tuple[int, int]]: Set of (row, col) tuples where the '42'
            pattern should be drawn.
    """
    pattern_width = 7
    pattern_height = 5

    if width < 9 or height < 7:
        return set()

    start_col = (width - pattern_width + (1 if width % 2 == 0 else 0)) // 2
    start_row = (height - pattern_height) // 2

    pattern: set[tuple[int, int]] = set()
    for dx, dy in PATTERN_42:
        pattern.add((start_row + dy, start_col + dx))
    return pattern
