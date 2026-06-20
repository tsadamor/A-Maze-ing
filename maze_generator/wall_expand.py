import random
from enum import IntEnum

from utils import maze_solver
from utils.patterns import get_pattern_42


class Direction(IntEnum):
    NORTH = 1 << 0
    EAST = 1 << 1
    SOUTH = 1 << 2
    WEST = 1 << 3


def gen_maze_wall_expand(width: int, height: int) -> list[list[int]]:
    maze = [[0] * width for _ in range(height)]
    connected_pillars = set()

    blocked_cells = get_pattern_42(width, height)
    if blocked_cells:
        for cx, cy in blocked_cells:
            connected_pillars.update(
                [(cy, cx), (cy + 1, cx), (cy, cx + 1), (cy + 1, cx + 1)]
            )
            maze[cy][cx] = 15

            if cy > 0:
                maze[cy - 1][cx] |= Direction.SOUTH  # 北側のマスの「南壁」
            if cy < height - 1:
                maze[cy + 1][cx] |= Direction.NORTH  # 南側のマスの「北壁」
            if cx > 0:
                maze[cy][cx - 1] |= Direction.EAST  # 西側のマスの「東壁」
            if cx < width - 1:
                maze[cy][cx + 1] |= Direction.WEST

    for w in range(width):
        maze[0][w] |= Direction.NORTH
        maze[height - 1][w] |= Direction.SOUTH
        connected_pillars.update([(0, w), (0, w + 1), (height, w), (height, w + 1)])

    for h in range(height):
        maze[h][0] |= Direction.WEST
        maze[h][width - 1] |= Direction.EAST
        connected_pillars.update([(h, 0), (h + 1, 0), (h, width), (h + 1, width)])

    remaining_pillars = [(h, w) for h in range(1, height) for w in range(1, width)]
    random.shuffle(remaining_pillars)

    while remaining_pillars:
        start_h, start_w = remaining_pillars.pop()

        if (start_h, start_w) in connected_pillars:
            continue

        ph, pw = start_h, start_w
        path_history = [(ph, pw)]
        temp_walls = []

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
                    for from_h, from_w, to_h, to_w in temp_walls:
                        if from_w == to_w:
                            min_h = min(from_h, to_h)
                            if from_w > 0:
                                maze[min_h][from_w - 1] |= Direction.EAST
                            if from_w < width:
                                maze[min_h][from_w] |= Direction.WEST

                        else:
                            min_w = min(from_w, to_w)
                            if from_h > 0:
                                maze[from_h - 1][min_w] |= Direction.SOUTH
                            if from_h < height:
                                maze[from_h][min_w] |= Direction.NORTH

                    for p in path_history:
                        connected_pillars.add(p)

                    moved = True
                    break
                else:
                    ph, pw = nh, nw
                    moved = True
                    break

            if not moved:
                break
            if (nh, nw) in connected_pillars:
                break

    return maze


def print_ascii_maze(
    grid: list[list[int]], entry: tuple[int, int], exit_coord: tuple[int, int]
) -> None:
    if not grid:
        return

    height = len(grid)
    width = len(grid[0])

    canvas_height = 2 * height + 1
    canvas_width = 2 * width + 1
    canvas = [["##" for _ in range(canvas_width)] for _ in range(canvas_height)]

    for y in range(height):
        for x in range(width):
            cy = 2 * y + 1
            cx = 2 * x + 1

            cell_value = grid[y][x]

            # 完全に閉じられた42の岩盤（15）なら、周囲3x3を含めて ██ で上書き
            if cell_value == 15:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        canvas[cy + dy][cx + dx] = "██"
                continue

            # 普通の通路の床
            canvas[cy][cx] = "  "

            # 各方向のビットを見て、壁がない（0）なら通路（空白）にする
            if not (cell_value & Direction.NORTH):
                canvas[cy - 1][cx] = "  "
            if not (cell_value & Direction.EAST):
                canvas[cy][cx + 1] = "  "
            if not (cell_value & Direction.SOUTH):
                canvas[cy + 1][cx] = "  "
            if not (cell_value & Direction.WEST):
                canvas[cy][cx - 1] = "  "

    # 入口と出口を上書き
    entry_x, entry_y = entry
    exit_x, exit_y = exit_coord
    canvas[2 * entry_y + 1][2 * entry_x + 1] = "ST"
    canvas[2 * exit_y + 1][2 * exit_x + 1] = "ED"

    for row in canvas:
        print("".join(row))


# 💡【ここを追加！】単体テスト用のメイン処理
if __name__ == "__main__":
    import sys

    width = 7
    height = 7
    entry = (0, 0)
    exit_coord = (width - 1, height - 1)

    if len(sys.argv) == 3:
        width = int(sys.argv[1])
        height = int(sys.argv[2])
        exit_coord = (width - 1, height - 1)

    print(f"--- Generating Wall-Expand Maze ({width} x {height}) ---")
    generated_maze = gen_maze_wall_expand(width, height)

    print("\n--- Visualized ASCII Maze ---")
    print_ascii_maze(generated_maze, entry, exit_coord)

    hex_char = "0123456789ABCDEF"
    with open("maze.txt", "w", encoding="utf-8") as f:
        for h in range(height):
            for w in range(width):
                print(hex_char[generated_maze[h][w]], end="", file=f)
            print(file=f)

        print(file=f)
        print(f"{entry[0]},{entry[1]}", file=f)
        print(f"{exit_coord[0]},{exit_coord[1]}", file=f)
        solve_res = maze_solver(generated_maze, width, height, entry, exit_coord)
        print(solve_res, file=f)
