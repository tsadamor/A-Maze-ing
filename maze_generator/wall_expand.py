import random
import tkinter as tk
from enum import IntEnum


class Direction(IntEnum):
    NORTH = 1 << 0
    EAST = 1 << 1
    SOUTH = 1 << 2
    WEST = 1 << 3


def gen_maze_wall_expand(width: int, height: int) -> list[list[int]]:
    maze = [[0] * width for _ in range(height)]

    connected_pillars = set()

    for x in range(width):
        maze[0][x] |= Direction.NORTH
        maze[height - 1][x] |= Direction.SOUTH
        connected_pillars.update([(x, 0), (x + 1, 0), (x, height), (x + 1, height)])

    for y in range(height):
        maze[y][0] |= Direction.WEST
        maze[y][width - 1] |= Direction.EAST
        connected_pillars.update([(0, y), (0, y + 1), (width, y), (width, y + 1)])

    remaining_pillars = []
    for y in range(1, height):
        for x in range(1, width):
            remaining_pillars.append((x, y))

    random.shuffle(remaining_pillars)

    while remaining_pillars:
        start_x, start_y = remaining_pillars.pop()

        if (start_x, start_y) in connected_pillars:
            continue

        px, py = start_x, start_y
        path_history = [(px, py)]
        temp_walls = []

        while True:
            dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            random.shuffle(dirs)

            moved = False
            for dx, dy in dirs:
                nx, ny = px + dx, py + dy

                if not (0 <= nx <= width and 0 <= ny <= height):
                    continue

                if (nx, ny) in path_history:
                    continue

                temp_walls.append((px, py, nx, ny))
                path_history.append((nx, ny))

                if (nx, ny) in connected_pillars:
                    for ax, ay, bx, by in temp_walls:
                        if ax == bx:
                            min_y = min(ay, by)
                            if ax > 0:
                                maze[min_y][ax - 1] |= Direction.EAST
                            if ax < width:
                                maze[min_y][ax] |= Direction.WEST
                        else:
                            min_x = min(ax, bx)
                            if ay > 0:
                                maze[ay - 1][min_x] |= Direction.SOUTH
                            if ay < height:
                                maze[ay][min_x] |= Direction.NORTH

                    for p in path_history:
                        connected_pillars.add(p)

                    moved = True
                    break

                else:
                    px, py = nx, ny
                    moved = True
                    break

            if not moved:
                break

            if (nx, ny) in connected_pillars:
                break

    return maze


def draw_maze(maze: list[list[int]], cell_size: int = 40):
    height = len(maze)
    width = len(maze[0])

    root = tk.Tk()
    root.title("Wall-Extension Maze Viewer")

    padding = 15
    canvas_w = width * cell_size + padding * 2
    canvas_h = height * cell_size + padding * 2

    canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
    canvas.pack()

    inner_thickness = 2
    outer_thickness = 4
    wall_color = "black"

    for h in range(height):
        for w in range(width):
            x1 = padding + w * cell_size
            y1 = padding + h * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size
            value = maze[h][w]

            if value & Direction.NORTH:
                canvas.create_line(
                    x1, y1, x2, y1, width=inner_thickness, fill=wall_color
                )
            if value & Direction.EAST:
                canvas.create_line(
                    x2, y1, x2, y2, width=inner_thickness, fill=wall_color
                )
            if value & Direction.SOUTH:
                canvas.create_line(
                    x1, y2, x2, y2, width=inner_thickness, fill=wall_color
                )
            if value & Direction.WEST:
                canvas.create_line(
                    x1, y1, x1, y2, width=inner_thickness, fill=wall_color
                )

    canvas.create_rectangle(
        padding,
        padding,
        padding + width * cell_size,
        padding + height * cell_size,
        width=outer_thickness,
        outline=wall_color,
    )

    root.mainloop()


if __name__ == "__main__":
    W, H = 20, 16
    maze_data = gen_maze_wall_expand(W, H)
    draw_maze(maze_data, cell_size=25)
