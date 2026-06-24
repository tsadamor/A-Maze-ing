from mlx import Mlx

from maze_generator import MazeGenerator
from maze_solver import MazeSolver
from parser import parser

CONF_FILE_NAME = "config.txt"

NORTH = 1 << 0
EAST = 1 << 1
SOUTH = 1 << 2
WEST = 1 << 3


def visualize_maze(maze, width=1600, height=1200):
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
    visualize_maze(maze)


if __name__ == "__main__":
    main()
