DIR_MAZE = [-1, 0, 1, 0, -1]
DIR = ["N", "E", "S", "W"]
DIR_WALL = [0, 1, 2, 3]


class MazeSolver:
    def __init__(
        self,
        maze: list[list[int]],
        file_name: str,
        enter: tuple[int, int],
        exit_coord: tuple[int, int],
        width: int,
        height: int,
    ):
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
        enter: tuple[int, int],
        exit_coord: tuple[int, int],
    ) -> str:
        def is_valid_coord(h, w) -> bool:
            if 0 <= h < height and 0 <= w < width:
                return True
            return False

        queue: list[tuple[int, int], str] = []
        queue.append((enter, ""))
        visited = [[False] * width for _ in range(height)]
        visited[enter[0]][enter[1]] = True
        result = ""
        found = False
        while len(queue):
            coord, ans = queue.pop(0)
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

    def write_to_file(self):
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
