import random

from mlx import Mlx
from utils.patterns import get_pattern_42

WIDTH = 800
HEIGHT = 600

NORTH = 1 << 0
EAST = 1 << 1
SOUTH = 1 << 2
WEST = 1 << 3


def visualize_maze(maze, width=800, height=600):
    rows = len(maze)
    cols = len(maze[0])

    cell_size = min(width // (cols + 2), height // (rows + 2))

    m = Mlx()
    p = m.mlx_init()

    win = m.mlx_new_window(p, width, height, "Maze Viewer")

    img = m.mlx_new_image(p, width, height)

    img_data, bpp, line_size, endian = m.mlx_get_data_addr(img)

    def put_pixel(x, y, r=255, g=255, b=255):
        if not (0 <= x < width and 0 <= y < height):
            return

        idx = y * line_size + x * (bpp // 8)

        img_data[idx] = b
        img_data[idx + 1] = g
        img_data[idx + 2] = r
        img_data[idx + 3] = 255

    def draw_line(x0, y0, x1, y1, r=255, g=255, b=255):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:
            put_pixel(x0, y0, r, g, b)

            if x0 == x1 and y0 == y1:
                break

            e2 = err * 2

            if e2 > -dy:
                err -= dy
                x0 += sx

            if e2 < dx:
                err += dx
                y0 += sy

    maze_w = cols * cell_size
    maze_h = rows * cell_size

    offset_x = (width - maze_w) // 2
    offset_y = (height - maze_h) // 2

    for y in range(rows):
        for x in range(cols):
            cell = maze[y][x]

            x0 = offset_x + x * cell_size
            y0 = offset_y + y * cell_size

            x1 = x0 + cell_size
            y1 = y0 + cell_size

            if cell & NORTH:
                draw_line(x0, y0, x1, y0)

            if cell & EAST:
                draw_line(x1, y0, x1, y1)

            if cell & SOUTH:
                draw_line(x0, y1, x1, y1)

            if cell & WEST:
                draw_line(x0, y0, x0, y1)

    m.mlx_put_image_to_window(p, win, img, 0, 0)

    m.mlx_do_sync(p)

    def cleanup():
        m.mlx_destroy_image(p, img)
        m.mlx_destroy_window(p, win)
        m.mlx_loop_exit(p)

    def on_key(keynum, param):
        if keynum == 65307:
            cleanup()

    def on_close(param):
        cleanup()

    m.mlx_key_hook(win, on_key, None)
    m.mlx_hook(win, 33, 0, on_close, None)

    m.mlx_loop(p)


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


def print_ascii_maze(
    grid: list[list[int]], entry: tuple[int, int], exit_coord: tuple[int, int]
) -> None:
    """
    grid データを読み込み、壁を『#』、通路を『  』で描きつつ、
    入口を『ST』、出口を『ED』としてターミナルに出力する関数
    """
    if not grid:
        return

    height = len(grid)
    width = len(grid[0])

    # 1. 「2倍 + 1」のサイズで、すべて壁（"##"）で埋まったキャンバスを作成
    canvas_height = 2 * height + 1
    canvas_width = 2 * width + 1
    canvas = [["##" for _ in range(canvas_width)] for _ in range(canvas_height)]

    # 2. 元の迷路を1マスずつチェックしてキャンバスを削る
    for y in range(height):
        for x in range(width):
            cy = 2 * y + 1
            cx = 2 * x + 1

            cell_value = grid[y][x]

            if cell_value == 15:
                # 中心、上下左右、さらに「斜めの角」もすべて含めて 3x3 を ██ で塗りつぶ
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        canvas[cy + dy][cx + dx] = "██"
                continue  # 中心を通路（空白）にする
            canvas[cy][cx] = "  "

            # 各方向のビットをチェックして壁をぶち抜く
            if not (cell_value & (1 << 0)):  # 北
                canvas[cy - 1][cx] = "  "
            if not (cell_value & (1 << 1)):  # 東
                canvas[cy][cx + 1] = "  "
            if not (cell_value & (1 << 2)):  # 南
                canvas[cy + 1][cx] = "  "
            if not (cell_value & (1 << 3)):  # 西
                canvas[cy][cx - 1] = "  "

    # 3. 【追加】入口と出口の座標に目印（2文字）を上書きする
    entry_x, entry_y = entry
    exit_x, exit_y = exit_coord

    canvas[2 * entry_y + 1][2 * entry_x + 1] = "ST"  # Start (入口)
    canvas[2 * exit_y + 1][2 * exit_x + 1] = "ED"  # End (出口)

    # 4. 画面に出力
    for row in canvas:
        print("".join(row))


if __name__ == "__main__":
    import sys

    width = 100
    height = 100
    entry = (0, 0)
    # 出口を右下のマスに設定
    exit_coord = (width - 1, height - 1)

    if len(sys.argv) == 3:
        width = int(sys.argv[1])
        height = int(sys.argv[2])
        # 引数でサイズが変わった場合も、自動で右下にゴールを設定
        exit_coord = (width - 1, height - 1)

    print(f"--- Generating Maze ({width} x {height}) ---")
    generated_grid = generate_maze_dfs(width, height, entry)

    # print("\n--- Visualized ASCII Maze ---")
    # 引数に入口と出口を足して呼び出す
    # print_ascii_maze(generated_grid, entry, exit_coord)
    visualize_maze(generated_grid)
