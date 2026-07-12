"""Maze solver module using breadth-first search.

This module provides the `MazeSolver` class, which calculates the
shortest path from an entry cell to an exit cell in a given 2D grid of
wall masks. It uses a Breadth-First Search (BFS) algorithm, guaranteeing
that the shortest path is found.

Graph Representation & Wall Encoding:
-------------------------------------
The maze is modeled as a grid of cell nodes where open walls are the
graph edges. Each cell has an integer value between 0 and 15 representing
its walls as bitwise flags:
  - Bit 0 (val 1): North wall is closed
  - Bit 1 (val 2): East wall is closed
  - Bit 2 (val 4): South wall is closed
  - Bit 3 (val 8): West wall is closed

If a wall flag is unset (0), the passage is open, allowing traversal
to the adjacent cell. Otherwise, the passage is blocked.

Usage Example:
--------------
    from mazegen.maze_solver import MazeSolver

    # 1. Provide a 2x2 maze grid:
    # Row 0: cell 0 (N, W closed -> 9), cell 1 (N, E closed -> 3)
    # Row 1: cell 0 (S, W closed -> 12), cell 1 (S, E closed -> 6)
    # (Passage exists vertically between (0,0)-(1,0), (0,1)-(1,1)
    # and horizontally (0,0)-(0,1), (1,0)-(1,1))
    # Wait, let's say the wall between (0,0) and (0,1) is open:
    # (0,0): North & West closed -> 9
    # (0,1): North & East closed -> 3
    # The solver will navigate using these open paths.
    maze_grid = [
        [9, 3],
        [12, 6]
    ]

    # 2. Initialize the solver
    solver = MazeSolver(
        maze=maze_grid,
        file_name="solution.txt",
        entry_coord=(0, 0),
        exit_coord=(1, 1),
        width=2,
        height=2
    )

    # 3. Solve the maze to get the direction string
    path = solver.solve_maze()
    # e.g., "SE" or "ES" depending on layout
    print("Shortest path directions:", path)
"""

from collections import deque
from mazegen.utils import DIR_MAZE, DIR_NAMES


class MazeSolver:
    """Finds the shortest path through a 2D grid representation of a maze.

    Explores all reachable paths from the specified start point ('entry_coord')
    to the destination ('exit_coord') and caches the result for future queries.

    Attributes:
        maze (list[list[int]]): 2D list of wall masks where set bits indicate
            closed walls.
        file_name (str): Path to the output file where output results might
            be saved.
        entry_coord (tuple[int, int]): Start coordinate formatted as
            (row, col).
        exit_coord (tuple[int, int]): End coordinate formatted as (row, col).
        width (int): Number of columns in the maze grid.
        height (int): Number of rows in the maze grid.
    """

    def __init__(
        self,
        maze: list[list[int]],
        file_name: str,
        entry_coord: tuple[int, int],
        exit_coord: tuple[int, int],
        width: int,
        height: int,
    ) -> None:
        """Initialize MazeSolver.

        Args:
            maze (list[list[int]]): 2D list of wall masks.
            file_name (str): Path to output file.
            entry_coord (tuple[int, int]): Start coordinates (row, col).
            exit_coord (tuple[int, int]): End coordinates (row, col).
            width (int): Maze width.
            height (int): Maze height.
        """
        self.maze = maze
        self.file_name = file_name
        self.entry_coord = entry_coord
        self.exit_coord = exit_coord
        self.width = width
        self.height = height
        self._cached_path: str | None = None

    def solve_maze(self) -> str:
        """Find shortest valid path from entry_coord to exit_coord using BFS.

        Returns:
            str: String of directions ('N', 'E', 'S', 'W') for shortest path.
        """
        if self._cached_path is not None:
            return self._cached_path

        def is_valid_coord(row: int, col: int) -> bool:
            """Check if coordinate is within maze boundaries."""
            return 0 <= row < self.height and 0 <= col < self.width

        queue: deque[tuple[tuple[int, int], str]] = deque(
            [(self.entry_coord, "")]
        )
        visited = [[False] * self.width for _ in range(self.height)]
        visited[self.entry_coord[0]][self.entry_coord[1]] = True
        result = ""
        found = False

        while queue:
            current_coord, current_path = queue.popleft()
            row, col = current_coord[0], current_coord[1]
            for d in range(4):
                next_row, next_col = row + DIR_MAZE[d], col + DIR_MAZE[d + 1]
                if not is_valid_coord(next_row, next_col) or visited[
                    next_row
                ][next_col]:
                    continue
                # Bit positions: N=0, E=1, S=2, W=3
                if self.maze[row][col] & (1 << d):
                    continue
                visited[next_row][next_col] = True
                if (next_row, next_col) == self.exit_coord:
                    result = current_path + DIR_NAMES[d]
                    found = True
                    break
                queue.append(
                    ((next_row, next_col), current_path + DIR_NAMES[d])
                )
            if found:
                break

        self._cached_path = result
        return result
