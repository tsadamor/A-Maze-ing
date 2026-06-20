PATTERN_42 = [
        (-2, -2), (-2, -1), (-2, 0),
        (-1, 0),
        (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),

        (2, -2), (3, -2), (4, -2),
        (4, -1),
        (4, 0), (3, 0), (2, 0),
        (2, 1),
        (2, 2), (3, 2), (4, 2)
        ]


def get_pattern_42(width: int, height: int) -> set[tuple[int, int]]:
    center_x = width // 2
    center_y = height // 2

    if (
        center_x - 2 < 0 or center_x + 4 >= width
        or center_y - 2 < 0 or center_y + 2 >= height
    ):
        return set()

    pattern = set()
    for dx, dy in PATTERN_42:
        abs_x = center_x + dx
        abs_y = center_y + dy
        pattern.add((abs_x, abs_y))
    return pattern
