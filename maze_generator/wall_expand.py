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

    for w in range(width):
        maze[0][w] |= Direction.NORTH
        maze[height - 1][w] |= Direction.SOUTH
        connected_pillars.update([(w, 0), (w + 1, 0), (w, height), (w + 1, height)])

    for h in range(height):
        maze[h][0] |= Direction.WEST
        maze[h][width - 1] |= Direction.EAST
        connected_pillars.update([(0, h), (0, h + 1), (width, h), (width, h + 1)])

    remaining_pillars = []
    for h in range(1, height):
        for w in range(1, width):
            remaining_pillars.append((w, h))

    random.shuffle(remaining_pillars)

    while remaining_pillars:
        start_w, start_h = remaining_pillars.pop()

        if (start_w, start_h) in connected_pillars:
            continue

        pw, ph = start_w, start_h
        path_history = [(pw, ph)]
        temp_walls = []

        while True:
            dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
            random.shuffle(dirs)

            moved = False
            for dw, dh in dirs:
                nw, nh = pw + dw, ph + dh

                if not (0 <= nw <= width and 0 <= nh <= height):
                    continue

                if (nw, nh) in path_history:
                    continue

                temp_walls.append((pw, ph, nw, nh))
                path_history.append((nw, nh))

                if (nw, nh) in connected_pillars:
                    for from_w, from_h, to_w, to_h in temp_walls:
                        if from_w == to_w:
                            min_y = min(from_h, to_h)
                            if from_w > 0:
                                maze[min_y][from_w - 1] |= Direction.EAST
                            if from_w < width:
                                maze[min_y][from_w] |= Direction.WEST
                        else:
                            min_x = min(from_w, to_w)
                            if from_h > 0:
                                maze[from_h - 1][min_x] |= Direction.SOUTH
                            if from_h < height:
                                maze[from_h][min_x] |= Direction.NORTH

                    for p in path_history:
                        connected_pillars.add(p)

                    moved = True
                    break

                else:
                    pw, ph = nw, nh
                    moved = True
                    break

            if not moved:
                break

            if (nw, nh) in connected_pillars:
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
