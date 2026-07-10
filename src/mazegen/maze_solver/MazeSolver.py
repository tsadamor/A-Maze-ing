"""Maze solver module using breadth-first search."""

from collections import deque
from src.mazegen.maze_generator.utils import DIR_MAZE, DIR_NAMES


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

    def solve_maze(self) -> str:
        """Find shortest valid path from enter to exit_coord using BFS.

        Returns:
            str: String of directions ('N', 'E', 'S', 'W') for shortest path.
        """
        def is_valid_coord(h: int, w: int) -> bool:
            """Check if coordinate is within maze boundaries."""
            return 0 <= h < self.height and 0 <= w < self.width

        queue: deque[tuple[tuple[int, int], str]] = deque([(self.enter, "")])
        visited = [[False] * self.width for _ in range(self.height)]
        visited[self.enter[0]][self.enter[1]] = True
        result = ""
        found = False

        while queue:
            coord, ans = queue.popleft()
            h, w = coord[0], coord[1]
            for d in range(4):
                nh, nw = h + DIR_MAZE[d], w + DIR_MAZE[d + 1]
                if not is_valid_coord(nh, nw) or visited[nh][nw]:
                    continue
                # Bit positions: N=0, E=1, S=2, W=3
                if self.maze[h][w] & (1 << d):
                    continue
                visited[nh][nw] = True
                if (nh, nw) == self.exit_coord:
                    result = ans + DIR_NAMES[d]
                    found = True
                    break
                queue.append(((nh, nw), ans + DIR_NAMES[d]))
            if found:
                break

        return result
