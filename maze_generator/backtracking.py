import random

from maze_generator.utils import get_pattern_42

NORTH = 1 << 0
EAST = 1 << 1
SOUTH = 1 << 2
WEST = 1 << 3

Maze = list[list[int]]
StepDiff = list[tuple[int, int, int]]
AnimationSteps = tuple[Maze, list[StepDiff]]


def generate_maze_dfs(
    width: int, height: int, entry: tuple[int, int]
) -> list[list[int]]:
    grid = [[15 for _ in range(width)] for _ in range(height)]
    directions = [(0, 0, -1), (1, 1, 0), (2, 0, 1), (3, -1, 0)]
    stack = [entry]
    visited = {entry}
    blocked_area = get_pattern_42(width, height)

    if blocked_area:
        visited.update(blocked_area)

    while stack:
        current = stack[-1]
        x, y = current
        valid_neighbors = []

        for bit_pos, dx, dy in directions:
            nx = x + dx
            ny = y + dy
            if (
                nx >= 0
                and nx < width
                and ny >= 0
                and ny < height
                and (nx, ny) not in visited
            ):
                valid_neighbors.append((bit_pos, nx, ny))
        if valid_neighbors:
            new = random.choice(valid_neighbors)
        else:
            stack.pop()
            continue

        bit_pos, nx, ny = new
        opposit_bit_pos = (bit_pos + 2) % 4
        grid[y][x] ^= 1 << bit_pos
        grid[ny][nx] ^= 1 << opposit_bit_pos

        stack.append((nx, ny))
        visited.add((nx, ny))

    return grid


def generate_maze_dfs_with_steps(
    width: int,
    height: int,
    entry: tuple[int, int],
) -> tuple[Maze, AnimationSteps]:
    """バックトラッキングDFS法で迷路を生成し、(完成迷路, (初期状態, 差分リスト)) を返す。

    差分リストの各要素は [(y, x, new_value), ...] で、
    そのステップで変更されたセルだけを記録する。
    """
    grid = [[15 for _ in range(width)] for _ in range(height)]
    directions = [(0, 0, -1), (1, 1, 0), (2, 0, 1), (3, -1, 0)]
    stack = [entry]
    visited = {entry}
    blocked_area = get_pattern_42(width, height)

    if blocked_area:
        visited.update(blocked_area)

    # 全壁の初期状態を1回だけコピー
    initial = [row[:] for row in grid]
    diffs = []

    while stack:
        current = stack[-1]
        x, y = current
        valid_neighbors = []

        for bit_pos, dx, dy in directions:
            nx = x + dx
            ny = y + dy
            if (
                nx >= 0
                and nx < width
                and ny >= 0
                and ny < height
                and (nx, ny) not in visited
            ):
                valid_neighbors.append((bit_pos, nx, ny))
        if valid_neighbors:
            new = random.choice(valid_neighbors)
        else:
            stack.pop()
            continue

        bit_pos, nx, ny = new
        opposit_bit_pos = (bit_pos + 2) % 4
        grid[y][x] ^= 1 << bit_pos
        grid[ny][nx] ^= 1 << opposit_bit_pos

        stack.append((nx, ny))
        visited.add((nx, ny))

        # 変更された2セルの差分だけ記録
        diffs.append([(y, x, grid[y][x]), (ny, nx, grid[ny][nx])])

    return grid, (initial, diffs)
