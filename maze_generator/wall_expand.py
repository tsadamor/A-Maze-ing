import random
from enum import IntEnum

from mlx import Mlx

from maze_generator.utils import get_pattern_42

WIDTH = 800
HEIGHT = 600

NORTH = 1 << 0
EAST = 1 << 1
SOUTH = 1 << 2
WEST = 1 << 3


def visualize_maze(maze, width=3000, height=1500):
    rows = len(maze)
    cols = len(maze[0])
    cell_size = min(width // (cols + 2), height // (rows + 2))

    maze_w = cols * cell_size
    maze_h = rows * cell_size
    offset_x = (width - maze_w) // 2
    offset_y = (height - maze_h) // 2

    pattern_cells = get_pattern_42(cols, rows)

    m = Mlx()
    p = m.mlx_init()

    win = m.mlx_new_window(p, width, height, "Maze Viewer")

    img = m.mlx_new_image(p, width, height)

    img_data, bpp, line_size, endian = m.mlx_get_data_addr(img)

    def put_pixel(cx, cy, thickness=7):
        # 中心から上下左右にどれくらい太らせるか計算
        offset = thickness // 2
        cell_x = int((cx - offset_x) // cell_size)
        cell_y = int((cy - offset_y) // cell_size)
        # 元のコードにあったランダムな色の決定
        # c = min(round(0.06 * (cx + cy)), 255)
        r, g, b = 0, 200, 200
        if (cell_x, cell_y) in pattern_cells:
            r, g, b = 255, 0, 0

        # 中心(
        for dy in range(-offset, offset + 1):
            for dx in range(-offset, offset + 1):
                x = cx + dx
                y = cy + dy

                # 画面外にはみ出ないようにブロック
                if not (0 <= x < width and 0 <= y < height):
                    continue

                idx = y * line_size + x * (bpp // 8)

                img_data[idx] = b
                img_data[idx + 1] = g
                img_data[idx + 2] = r
                img_data[idx + 3] = 255

    def fill_rect(rx, ry, rw, rh, r, g, b):
        for y in range(ry, ry + rh):
            for x in range(rx, rx + rw):
                if not (0 <= x < width and 0 <= y < height):
                    continue

                idx = int(y * line_size + x * (bpp // 8))
                img_data[idx] = b
                img_data[idx + 1] = g
                img_data[idx + 2] = r
                img_data[idx + 3] = 255

    # === 3. 線を引く関数（put_pixelに色を渡すように修正） ===
    def draw_line(x0, y0, x1, y1, r=255, g=255, b=255):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            put_pixel(x0, y0)  # 色を渡す
            if x0 == x1 and y0 == y1:
                break
            e2 = err * 2
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    # === 4. 描画のメインループ ===
    maze_w = cols * cell_size
    maze_h = rows * cell_size
    offset_x = (width - maze_w) // 2
    offset_y = (height - maze_h) // 2

    # 42のパターンの座標を取得（迷路のマス目基準）
    pattern_cells = get_pattern_42(cols, rows)

    for y in range(rows):
        for x in range(cols):
            cell = maze[y][x]

            x0 = offset_x + x * cell_size
            y0 = offset_y + y * cell_size
            x1 = x0 + cell_size
            y1 = y0 + cell_size

            # 【追加】まず最初に背景（床）を塗る
            if (x, y) in pattern_cells:
                # 42の領域なら、マス全体をグレー(180, 180, 180)で塗りつぶす
                fill_rect(x0, y0, cell_size, cell_size, 255, 0, 0)

            # その後、壁（線）を白で描画する
            wall_r, wall_g, wall_b = 255, 255, 255

            if cell & NORTH:
                draw_line(x0, y0, x1, y0, wall_r, wall_g, wall_b)
            if cell & EAST:
                draw_line(x1, y0, x1, y1, wall_r, wall_g, wall_b)
            if cell & SOUTH:
                draw_line(x0, y1, x1, y1, wall_r, wall_g, wall_b)
            if cell & WEST:
                draw_line(x0, y0, x0, y1, wall_r, wall_g, wall_b)

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


def gen_maze_wall_expand_with_steps(width: int, height: int):
    """壁伸長法で迷路を生成し、(完成迷路, (初期状態, 差分リスト)) を返す。

    差分リストの各要素は [(y, x, new_value), ...] で、
    そのステップで変更されたセルだけを記録する。
    """
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
                maze[cy - 1][cx] |= Direction.SOUTH
            if cy < height - 1:
                maze[cy + 1][cx] |= Direction.NORTH
            if cx > 0:
                maze[cy][cx - 1] |= Direction.EAST
            if cx < width - 1:
                maze[cy][cx + 1] |= Direction.WEST

    # 外枠の壁を設定（初期状態）
    for w in range(width):
        maze[0][w] |= Direction.NORTH
        maze[height - 1][w] |= Direction.SOUTH
        connected_pillars.update([(0, w), (0, w + 1), (height, w), (height, w + 1)])

    for h in range(height):
        maze[h][0] |= Direction.WEST
        maze[h][width - 1] |= Direction.EAST
        connected_pillars.update([(h, 0), (h + 1, 0), (h, width), (h + 1, width)])

    # 外枠のみの状態を初期スナップショットとして1回だけコピー
    initial = [row[:] for row in maze]
    diffs = []

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
                    diff = []
                    for from_h, from_w, to_h, to_w in temp_walls:
                        if from_w == to_w:
                            min_h = min(from_h, to_h)
                            if from_w > 0:
                                maze[min_h][from_w - 1] |= Direction.EAST
                                diff.append((min_h, from_w - 1, maze[min_h][from_w - 1]))
                            if from_w < width:
                                maze[min_h][from_w] |= Direction.WEST
                                diff.append((min_h, from_w, maze[min_h][from_w]))

                        else:
                            min_w = min(from_w, to_w)
                            if from_h > 0:
                                maze[from_h - 1][min_w] |= Direction.SOUTH
                                diff.append((from_h - 1, min_w, maze[from_h - 1][min_w]))
                            if from_h < height:
                                maze[from_h][min_w] |= Direction.NORTH
                                diff.append((from_h, min_w, maze[from_h][min_w]))

                    for p in path_history:
                        connected_pillars.add(p)

                    # 変更セルの差分だけ記録
                    diffs.append(diff)

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

    return maze, (initial, diffs)


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

    width = 20
    height = 20
    entry = (0, 0)
    exit_coord = (width - 1, height - 1)

    if len(sys.argv) == 3:
        width = int(sys.argv[1])
        height = int(sys.argv[2])
        exit_coord = (width - 1, height - 1)

    print(f"--- Generating Wall-Expand Maze ({width} x {height}) ---")
    generated_maze = gen_maze_wall_expand(width, height)

    # print("\n--- Visualized ASCII Maze ---")
    # print_ascii_maze(generated_maze, entry, exit_coord)
    visualize_maze(generated_maze)
