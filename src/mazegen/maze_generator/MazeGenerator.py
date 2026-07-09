"""Maze generator module providing standalone MazeGenerator class."""

import random
import sys
from typing import Any

from src.mazegen.maze_solver import MazeSolver
from .backtracking import generate_maze_dfs, generate_maze_dfs_with_steps
from .braided import generate_maze_pacman, generate_maze_pacman_with_steps
from .wall_expand import gen_maze_wall_expand, gen_maze_wall_expand_with_steps


class MazeGenerator:
    """Standalone MazeGenerator class for creating perfect or Pac-Man mazes.

    Can be initialized either from a configuration dictionary or via keyword
    arguments.

    Attributes:
        width (int): Maze width in cells.
        height (int): Maze height in cells.
        entry (tuple[int, int]): Entry coordinate as (row, col).
        exit_coord (tuple[int, int]): Exit coordinate as (row, col).
        output_file (str): Output file path.
        perfect (bool): Whether to generate a perfect maze.
        seed (int | None): Optional random seed for reproducibility.
        algorithm (str | None): Specific algorithm
            ('dfs', 'pacman', 'wall_expand').
        maze (list[list[int]]): 2D list of integer wall masks.
    """

    def __init__(
        self,
        config: dict[str, Any] | None = None,
        *,
        width: int = 20,
        height: int = 15,
        entry: tuple[int, int] = (0, 0),
        exit_coord: tuple[int, int] = (14, 19),
        output_file: str = "maze.txt",
        perfect: bool = True,
        seed: int | None = None,
        algorithm: str | None = None,
    ) -> None:
        """Initialize MazeGenerator with config dictionary or params.

        Args:
            config (dict[str, Any] | None): Optional configuration dictionary.
            width (int): Maze width in cells.
            height (int): Maze height in cells.
            entry (tuple[int, int]): Entry coordinate as (row, col).
            exit_coord (tuple[int, int]): Exit coordinate as (row, col).
            output_file (str): Output file path.
            perfect (bool): Whether to generate a perfect maze.
            seed (int | None): Optional random seed for reproducibility.
            algorithm (str | None): Specific algorithm
                ('dfs', 'pacman', 'wall_expand').
        """
        if config is not None:
            self.width: int = config["WIDTH"]
            self.height: int = config["HEIGHT"]
            self.entry: tuple[int, int] = config["ENTRY"]
            self.exit_coord: tuple[int, int] = config["EXIT"]
            self.output_file: str = config["OUTPUT_FILE"]
            self.perfect: bool = config["PERFECT"]
            self.seed: int | None = config.get("SEED")
            self.algorithm: str | None = config.get("ALGORITHM")
        else:
            self.width = width
            self.height = height
            self.entry = entry
            self.exit_coord = exit_coord
            self.output_file = output_file
            self.perfect = perfect
            self.seed = seed
            self.algorithm = algorithm

        self.maze: list[list[int]] = []

    def _check_pattern_42_size(self) -> None:
        """Warn if maze size is too small to render the '42' pattern."""
        if self.width < 7 or self.height < 5:
            print(
                "Warning: Maze size too small to display '42' pattern.",
                file=sys.stderr,
            )

    def generate_maze(self) -> list[list[int]]:
        """Generate maze structure based on configuration.

        Returns:
            list[list[int]]: 2D list of integer wall masks.
        """
        self._check_pattern_42_size()
        if self.seed is not None:
            random.seed(self.seed)

        algo = self.algorithm.lower() if self.algorithm else None
        if algo == "dfs" or (algo is None and self.perfect):
            self.maze = generate_maze_dfs(self.width, self.height, self.entry)
        elif algo == "wall_expand":
            self.maze = gen_maze_wall_expand(self.width, self.height)
        else:
            self.maze = generate_maze_pacman(
                self.width, self.height, self.entry
            )
        return self.maze

    def generate_maze_steps(
        self,
    ) -> tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]:
        """Generate maze and return step history for visual animation.

        Returns:
            tuple[list[list[int]],
            tuple[list[list[int]], list[list[Any]]]]: A tuple containing:
                - list[list[int]]: The final grid.
                - tuple: A tuple of (initial grid copy, list of step diffs).
        """
        self._check_pattern_42_size()
        if self.seed is not None:
            random.seed(self.seed)

        algo = self.algorithm.lower() if self.algorithm else None
        if algo == "dfs" or (algo is None and self.perfect):
            self.maze, steps = generate_maze_dfs_with_steps(
                self.width, self.height, self.entry
            )
        elif algo == "wall_expand":
            self.maze, steps = gen_maze_wall_expand_with_steps(
                self.width, self.height
            )
        else:
            self.maze, steps = generate_maze_pacman_with_steps(
                self.width, self.height, self.entry
            )
        return self.maze, steps

    def get_maze(self) -> list[list[int]]:
        """Access generated maze structure, generating if needed.

        Returns:
            list[list[int]]: 2D list of integer wall masks.
        """
        if not self.maze:
            self.generate_maze()
        return self.maze

    def solve_maze(
        self,
        entry: tuple[int, int] | None = None,
        exit_coord: tuple[int, int] | None = None,
    ) -> str:
        """Solve maze and return directional path string ('N', 'E', 'S', 'W').

        Args:
            entry (tuple[int, int] | None): Optional start coordinate
                (defaults to configured entry).
            exit_coord (tuple[int, int] | None): Optional end coordinate
                (defaults to configured exit).

        Returns:
            str: String of directions representing shortest path.
        """
        if not self.maze:
            self.generate_maze()
        ent = entry if entry is not None else self.entry
        ext = exit_coord if exit_coord is not None else self.exit_coord
        solver = MazeSolver(
            self.maze, self.output_file, ent, ext, self.width, self.height
        )
        return solver.solve_maze(self.maze, self.width, self.height, ent, ext)

    def get_solution_path(
        self,
        entry: tuple[int, int] | None = None,
        exit_coord: tuple[int, int] | None = None,
    ) -> list[tuple[int, int]]:
        """Solve maze and return (row, col) path coordinates.

        Args:
            entry (tuple[int, int] | None): Optional start coordinate.
            exit_coord (tuple[int, int] | None): Optional end coordinate.

        Returns:
            list[tuple[int, int]]: List of (row, col) coordinates
                from entry to exit.
        """
        path_str = self.solve_maze(entry, exit_coord)
        ent = entry if entry is not None else self.entry
        coords = [ent]
        dir_deltas = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}
        curr = ent
        for d in path_str:
            dr, dc = dir_deltas[d]
            curr = (curr[0] + dr, curr[1] + dc)
            coords.append(curr)
        return coords

    def save_maze_to_file(self) -> None:
        """Save hexadecimal representation of maze rows to output file."""
        if not self.maze:
            return

        hex_char = "0123456789ABCDEF"
        with open(self.output_file, "w", encoding="utf-8") as f:
            for h in range(self.height):
                for w in range(self.width):
                    print(hex_char[self.maze[h][w]], end="", file=f)
                print(file=f)
