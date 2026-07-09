"""Maze solver module using breadth-first search."""

DIR_MAZE = [-1, 0, 1, 0, -1]
DIR = ["N", "E", "S", "W"]
DIR_WALL = [0, 1, 2, 3]


class MazeSolver:
    """Solver class that finds the shortest path through a maze using BFS.

    Attributes:
        maze (list[list[int]]): 2D list of wall masks.
        file_name (str): Path to output file.
        enter (tuple[int, int]): Start coordinates (row, col).
        exit_coord (tuple[int, int]): End coordinates (row, col).
        width (int): Maze width.
        height (int): Maze height.
    """

    def __init__(
        self,
        maze: list[list[int]],
        file_name: str,
        enter: tuple[int, int],
        exit_coord: tuple[int, int],
        width: int,
        height: int,
    ) -> None:
        """Initialize MazeSolver.

        Args:
            maze (list[list[int]]): 2D list of wall masks.
            file_name (str): Path to output file.
            enter (tuple[int, int]): Start coordinates (row, col).
            exit_coord (tuple[int, int]): End coordinates (row, col).
            width (int): Maze width.
            height (int): Maze height.
        """
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
        """Find shortest valid path from enter to exit_coord using BFS.

        Args:
            maze (list[list[int]]): 2D list of integer wall masks.
            width (int): Maze width.
            height (int): Maze height.
            enter (tuple[int, int]): Entry coordinates (row, col).
            exit_coord (tuple[int, int]): Exit coordinates (row, col).

        Returns:
            str: String of directions ('N', 'E', 'S', 'W') for shortest path.
        """
        def is_valid_coord(h: int, w: int) -> bool:
            """Check if coordinate is within maze boundaries.

            Args:
                h (int): Row index.
                w (int): Column index.

            Returns:
                bool: True if coordinate is inside the maze, False otherwise.
            """
            return 0 <= h < height and 0 <= w < width

        queue: list[tuple[tuple[int, int], str]] = [(enter, "")]
        visited = [[False] * width for _ in range(height)]
        visited[enter[0]][enter[1]] = True
        result = ""
        found = False

        while queue:
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

    def write_to_file(self) -> None:
        """Append entry/exit coordinates and shortest path to output file."""
        with open(self.file_name, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(f"{self.enter[1]},{self.enter[0]}\n")
            f.write(f"{self.exit_coord[1]},{self.exit_coord[0]}\n")
            solve_result = self.solve_maze(
                self.maze, self.width, self.height, self.enter, self.exit_coord
            )
            f.write(f"{solve_result}\n")
