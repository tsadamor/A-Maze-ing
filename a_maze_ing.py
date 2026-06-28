from enum import IntEnum

from mlx import Mlx

from maze_generator import MazeGenerator
from maze_generator.utils import get_pattern_42
from maze_solver import MazeSolver
from parser import parser

CONF_FILE_NAME = "config.txt"


class Directions(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3


DIR_MAZE = [-1, 0, 1, 0, -1]


def visualize_maze(maze, config, solver, width=3000, height=2000):
    m = Mlx()
    p = m.mlx_init()
    cmodes = [
        [255, 0, 0],
        [0, 255, 0],
        [0, 0, 255],
        [255, 255, 0],
        [255, 0, 255],
        [0, 255, 255],
        [255, 255, 255],
    ]

    win = m.mlx_new_window(p, width, height, "Maze Viewer")
    img = m.mlx_new_image(p, width, height)

    img_data, bpp, line_size, endian = m.mlx_get_data_addr(img)

    cell_size = 1
    offset_x = 0
    offset_y = 0
    cm = 0
    show_path = False
    pattern_cells = set()

    def put_pixel(cx, cy, cmode, thickness=7):
        offset = thickness // 2

        cell_x = int((cx - offset_x) // cell_size)
        cell_y = int((cy - offset_y) // cell_size)

        r, g, b = cmode[0], cmode[1], cmode[2]

        for dy in range(-offset, offset + 1):
            for dx in range(-offset, offset + 1):
                x = cx + dx
                y = cy + dy

                if not (0 <= x < width and 0 <= y < height):
                    continue

                idx = y * line_size + x * (bpp // 8)

                img_data[idx] = b
                img_data[idx + 1] = g
                img_data[idx + 2] = r
                img_data[idx + 3] = 255

    def draw_line(x0, y0, x1, y1, cmode):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:
            put_pixel(x0, y0, cmodes[cmode])

            if x0 == x1 and y0 == y1:
                break

            e2 = err * 2

            if e2 > -dy:
                err -= dy
                x0 += sx

            if e2 < dx:
                err += dx
                y0 += sy

    def clear_image():
        for y in range(height):
            for x in range(width):
                idx = y * line_size + x * (bpp // 8)

                img_data[idx] = 0
                img_data[idx + 1] = 0
                img_data[idx + 2] = 0
                img_data[idx + 3] = 255

    def fill_cell(x0, y0, x1, y1, cmode):
        """
        指定された矩形領域 (x0, y0) から (x1, y1) を指定した色で塗りつぶす
        rgb_color: [r, g, b] の配列 (例: [255, 0, 0])
        """
        r, g, b = cmodes[cmode]

        # ウィンドウの範囲外にはみ出さないようにガード（クリッピング）
        start_x = max(0, min(x0, width))
        end_x = max(0, min(x1, width))
        start_y = max(0, min(y0, height))
        end_y = max(0, min(y1, height))

        # 縦横のループでピクセルを愚直に埋める（一番高速）
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                idx = y * line_size + x * (bpp // 8)

                img_data[idx] = b
                img_data[idx + 1] = g
                img_data[idx + 2] = r
                img_data[idx + 3] = 255

    def render_maze(cmode, show_path):
        nonlocal cell_size
        nonlocal offset_x
        nonlocal offset_y

        rows = len(maze)
        cols = len(maze[0])

        cell_size = min(width // (cols + 2), height // (rows + 2))

        maze_w = cols * cell_size
        maze_h = rows * cell_size

        offset_x = (width - maze_w) // 2
        offset_y = (height - maze_h) // 2

        clear_image()

        pattern_cells = get_pattern_42(cols, rows)
        path_cells = []
        if show_path:
            path = solver.solve_maze(
                maze,
                cols,
                rows,
                config["ENTRY"],
                config["EXIT"],
            )
            w, h = config["ENTRY"]
            path_cells.append((w, h))
            for d in path:
                w += DIR_MAZE[Directions[d]]
                h += DIR_MAZE[Directions[d] + 1]
                path_cells.append((w, h))

        for y in range(rows):
            for x in range(cols):
                cell = maze[y][x]

                x0 = offset_x + x * cell_size
                y0 = offset_y + y * cell_size

                x1 = x0 + cell_size
                y1 = y0 + cell_size

                if (
                    (y, x) == config["ENTRY"]
                    or (y, x) == config["EXIT"]
                    or (x, y) in pattern_cells
                ):
                    fill_cell(x0, y0, x1, y1, (cmode + 1) % 7)
                elif (y, x) in path_cells:
                    fill_cell(x0, y0, x1, y1, (cmode + 2) % 7)
                if cell & 1 << Directions.N:
                    draw_line(x0, y0, x1, y0, cmode)

                if cell & 1 << Directions.E:
                    draw_line(x1, y0, x1, y1, cmode)

                if cell & 1 << Directions.S:
                    draw_line(x0, y1, x1, y1, cmode)

                if cell & 1 << Directions.W:
                    draw_line(x0, y0, x0, y1, cmode)

        m.mlx_put_image_to_window(p, win, img, 0, 0)

        text_y = height - 40

        m.mlx_string_put(
            p,
            win,
            50,
            text_y,
            0xFFFFFF,
            "[C]: Recoloring [R]: Regenerate [P] Path [Esc] Exit",
        )
        m.mlx_do_sync(p)

    def cleanup():
        m.mlx_destroy_image(p, img)
        m.mlx_destroy_window(p, win)
        m.mlx_loop_exit(p)

    def on_key(keynum, param):
        nonlocal maze
        nonlocal cm
        nonlocal show_path

        print(f"{keynum} key pressed")

        if keynum == 65307:
            cleanup()

        elif keynum == 114:
            maze = MazeGenerator(config).generate_maze()
            render_maze(cm, show_path)

        elif keynum == 99:
            cm = (cm + 1) % 7
            render_maze(cm, show_path)

        elif keynum == 112:
            show_path = not show_path
            render_maze(cm, show_path)

    def on_close(param):
        cleanup()

    render_maze(cm, show_path)

    m.mlx_key_hook(win, on_key, None)
    m.mlx_hook(win, 33, 0, on_close, None)

    m.mlx_loop(p)


def main():
    parse_result = parser(CONF_FILE_NAME)

    if not parse_result[0]:
        return

    config = parse_result[1]

    ent = config["ENTRY"]
    ext = config["EXIT"]
    wid = config["WIDTH"]
    hig = config["HEIGHT"]

    generator = MazeGenerator(config)
    maze = generator.generate_maze()

    generator.save_maze_to_file()

    solver = MazeSolver(maze, config["OUTPUT_FILE"], ent, ext, wid, hig)

    solver.write_to_file()

    visualize_maze(maze, config, solver)


if __name__ == "__main__":
    main()
