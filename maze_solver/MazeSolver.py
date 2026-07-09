import random
from collections import deque

Coord = tuple[int, int]
QueueItem = tuple[Coord, str]

DIR_MAZE = [-1, 0, 1, 0, -1]
DIR = ["N", "E", "S", "W"]
DIR_WALL = [0, 1, 2, 3]


class MazeSolver:
    def __init__(
        self,
        maze: list[list[int]],
        file_name: str,
        enter: Coord,
        exit_coord: Coord,
        width: int,
        height: int,
    ) -> None:
        self.maze = maze
        self.file_name = file_name
        self.enter = enter
        self.exit_coord = exit_coord
        self.width = width
        self.height = height

    def solve_maze(
        self,
        maze: list[list[int]],
        width: int,
        height: int,
        enter: Coord,
        exit_coord: Coord,
    ) -> str:
        def is_valid_coord(h: int, w: int) -> bool:
            if 0 <= h < height and 0 <= w < width:
                return True
            return False

        queue: deque[QueueItem] = deque()
        queue.append((enter, ""))
        visited = [[False] * width for _ in range(height)]
        visited[enter[0]][enter[1]] = True
        result = ""
        found = False
        while len(queue):
            coord, ans = queue.popleft()
            h, w = coord[0], coord[1]
            for d in range(4):
                nh, nw = h + DIR_MAZE[d], w + DIR_MAZE[d + 1]
                if not is_valid_coord(nh, nw) or visited[nh][nw]:
                    continue
                if maze[h][w] & (1 << DIR_WALL[d]):
                    continue
                visited[nh][nw] = True
                if (nh, nw) == exit_coord:
                    result = ans + DIR[d]
                    found = True
                    break
                queue.append(((nh, nw), ans + DIR[d]))
            if found:
                break
        return result

    def solve_random_maze(
        self,
        maze: list[list[int]],
        width: int,
        height: int,
        enter: Coord,
        exit_coord: Coord,
    ) -> str:
        def is_valid_coord(h: int, w: int) -> bool:
            if 0 <= h < height and 0 <= w < width:
                return True
            return False

        stack: list[QueueItem] = [(enter, "")]
        visited: set[Coord] = {enter}

        while stack:
            coord, ans = stack.pop()
            if coord == exit_coord:
                return ans

            h, w = coord
            directions = list(range(4))
            random.shuffle(directions)

            for d in directions:
                nh, nw = h + DIR_MAZE[d], w + DIR_MAZE[d + 1]
                if not is_valid_coord(nh, nw) or (nh, nw) in visited:
                    continue
                if maze[h][w] & (1 << DIR_WALL[d]):
                    continue
                visited.add((nh, nw))
                stack.append(((nh, nw), ans + DIR[d]))
        return ""

    def write_to_file(self) -> None:
        with open(self.file_name, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"{self.enter[0]},{self.enter[1]}")
            f.write("\n")
            f.write(f"{self.exit_coord[0]},{self.exit_coord[1]}")
            solve_result = self.solve_maze(
                self.maze, self.width, self.height, self.enter, self.exit_coord
            )
            f.write("\n")
            f.write((solve_result))
