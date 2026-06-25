from mlx import Mlx

from maze_generator import MazeGenerator
from maze_generator.utils import get_pattern_42
from maze_solver import MazeSolver
from parser import parser

CONF_FILE_NAME = "config.txt"

NORTH = 1 << 0
EAST = 1 << 1
SOUTH = 1 << 2
WEST = 1 << 3


def visualize_maze(maze, config, width=1600, height=1200):
    m = Mlx()
    p = m.mlx_init()

    win = m.mlx_new_window(p, width, height, "Maze Viewer")
    img = m.mlx_new_image(p, width, height)

    img_data, bpp, line_size, endian = m.mlx_get_data_addr(img)

    cell_size = 1
    offset_x = 0
    offset_y = 0
    cm = 0
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
        cmodes = [
            [255, 0, 0],
            [0, 255, 0],
            [0, 0, 255],
            [255, 255, 0],
            [255, 0, 255],
            [0, 255, 255],
            [255, 255, 255],
        ]

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

    def render_maze(cmode):
        nonlocal cell_size
        nonlocal offset_x
        nonlocal offset_y
        nonlocal pattern_cells

        rows = len(maze)
        cols = len(maze[0])

        cell_size = min(width // (cols + 2), height // (rows + 2))

        maze_w = cols * cell_size
        maze_h = rows * cell_size

        offset_x = (width - maze_w) // 2
        offset_y = (height - maze_h) // 2

        pattern_cells = get_pattern_42(cols, rows)

        clear_image()

        for y in range(rows):
            for x in range(cols):
                cell = maze[y][x]

                x0 = offset_x + x * cell_size
                y0 = offset_y + y * cell_size

                x1 = x0 + cell_size
                y1 = y0 + cell_size

                if cell & NORTH:
                    draw_line(x0, y0, x1, y0, cmode)

                if cell & EAST:
                    draw_line(x1, y0, x1, y1, cmode)

                if cell & SOUTH:
                    draw_line(x0, y1, x1, y1, cmode)

                if cell & WEST:
                    draw_line(x0, y0, x0, y1, cmode)

        m.mlx_put_image_to_window(p, win, img, 0, 0)
        m.mlx_do_sync(p)

    def cleanup():
        m.mlx_destroy_image(p, img)
        m.mlx_destroy_window(p, win)
        m.mlx_loop_exit(p)

    def on_key(keynum, param):
        nonlocal maze
        nonlocal cm

        print(f"{keynum} key pressed")

        if keynum == 65307:  # ESC
            cleanup()

        elif keynum == 114:  # r
            maze = MazeGenerator(config).generate_maze()
            render_maze(cm)

        elif keynum == 99:
            cm = (cm + 1) % 7
            render_maze(cm)

    def on_close(param):
        cleanup()

    render_maze(cm)

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

    visualize_maze(maze, config)


if __name__ == "__main__":
    main()
