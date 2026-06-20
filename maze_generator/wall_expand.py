import random
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
