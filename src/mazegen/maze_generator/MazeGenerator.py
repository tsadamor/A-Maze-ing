"""Maze generator module providing standalone MazeGenerator class.

This module provides the `MazeGenerator` class, which handles the generation
of various types of mazes (perfect mazes using Depth-First Search
or Wall Expansion, and playable braided mazes using a Pac-Man style
algorithm).

It supports customizing dimensions, random seed, entry/exit coordinates,
and output destinations.

How to use:
-----------
1. **Instantiate the generator**:
   Pass either a configuration dictionary (e.g. parsed from a config file) or
   direct keyword arguments (e.g., `width`, `height`, `seed`, etc.).

2. **Generate the maze**:
   Call `generate_maze()` to produce the structure.

3. **Access the structure**:
   Access the grid via the returned value or `get_maze()`. The structure is a
   2D list of integer wall masks.

4. **Access the solution**:
   Get the shortest path either as a string of cardinal directions
   ('N', 'E', 'S', 'W') via `solve_maze()` or as a sequence of `(row, col)`
   coordinate tuples via `get_solution_path()`.

Example:
--------
    from src.mazegen.maze_generator import MazeGenerator

    # Create a 20x15 perfect maze with a seed
    generator = MazeGenerator(
        width=20,
        height=15,
        entry=(0, 0),
        exit_coord=(14, 19),
        perfect=True,
        seed=42,
        algorithm="dfs"
    )

    # Generate the grid structure
    grid = generator.generate_maze()

    # Access the generated grid cell (row 0, col 0)
    start_cell_mask = grid[0][0]

    # Access the solution path
    path_directions = generator.solve_maze()  # entry.g. "SSEEES..."
    # entry.g. [(0,0), (1,0), ...]
    path_coordinates = generator.get_solution_path()
"""

import random
import sys
from typing import Any, Callable

from src.mazegen.maze_solver import MazeSolver
from .backtracking import generate_maze_dfs, generate_maze_dfs_with_steps
from .braided import generate_maze_pacman, generate_maze_pacman_with_steps
from .wall_expand import gen_maze_wall_expand, gen_maze_wall_expand_with_steps


def _wall_expand_wrapper(
    width: int, height: int, entry: tuple[int, int]
) -> list[list[int]]:
    return gen_maze_wall_expand(width, height)


def _wall_expand_steps_wrapper(
    width: int, height: int, entry: tuple[int, int]
) -> tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]:
    return gen_maze_wall_expand_with_steps(width, height)


# Mapping for extensible algorithm registration
_ALGORITHMS: dict[
    str, Callable[[int, int, tuple[int, int]], list[list[int]]]
] = {
    "dfs": generate_maze_dfs,
    "wall_expand": _wall_expand_wrapper,
    "pacman": generate_maze_pacman,
}

_ALGORITHMS_WITH_STEPS: dict[
    str,
    Callable[
        [int, int, tuple[int, int]],
        tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]],
    ],
] = {
    "dfs": generate_maze_dfs_with_steps,
    "wall_expand": _wall_expand_steps_wrapper,
    "pacman": generate_maze_pacman_with_steps,
}


class MazeGenerator:
    """A configurable maze generator for perfect and braided mazes.

    Instantiates a generator that can create standard perfect mazes (using
    DFS or Wilson's Wall Expansion) or multi-route playable boards containing
    loops.

    To instantiate, you can either provide:
      - A dictionary matching the configuration file format (all uppercase
        keys).
      - Direct keyword arguments.

    Attributes:
        width (int): Maze width in cells (number of columns).
        height (int): Maze height in cells (number of rows).
        entry (tuple[int, int]): Entry coordinate as (row, col).
        exit_coord (tuple[int, int]): Exit coordinate as (row, col).
        output_file (str): Output file path to save the generated maze.
        perfect (bool): True to generate a perfect maze (no loops, single
            path), False to generate a braided playable maze.
        seed (int | None): Optional random seed for deterministic generation.
        algorithm (str | None): Specific algorithm type ('dfs', 'pacman',
            'wall_expand').
        maze (list[list[int]]): 2D list of integer wall masks. Each cell is
            represented by a 4-bit integer mask indicating closed walls:
                - Bit 0 (val 1): North wall is closed
                - Bit 1 (val 2): East wall is closed
                - Bit 2 (val 4): South wall is closed
                - Bit 3 (val 8): West wall is closed
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
        if self.width < 9 or self.height < 7:
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

        algo = (
            self.algorithm.lower()
            if self.algorithm
            else ("dfs" if self.perfect else "pacman")
        )
        generator = _ALGORITHMS.get(algo, generate_maze_pacman)
        self.maze = generator(self.width, self.height, self.entry)
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

        algo = (
            self.algorithm.lower()
            if self.algorithm
            else ("dfs" if self.perfect else "pacman")
        )
        generator = _ALGORITHMS_WITH_STEPS.get(
            algo, generate_maze_pacman_with_steps
        )
        self.maze, steps = generator(self.width, self.height, self.entry)
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
        entry_coord = entry if entry is not None else self.entry
        exit_coord = exit_coord if exit_coord is not None else self.exit_coord
        solver = MazeSolver(
            self.maze,
            self.output_file,
            entry_coord,
            exit_coord,
            self.width,
            self.height
        )
        return solver.solve_maze()

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
        entry_coord = entry if entry is not None else self.entry
        coords = [entry_coord]
        dir_deltas = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "W": (0, -1)}
        current_coord = entry_coord
        for d in path_str:
            delta_row, delta_col = dir_deltas[d]
            current_coord = (
                current_coord[0] + delta_row,
                current_coord[1] + delta_col
            )
            coords.append(current_coord)
        return coords

    def save_maze_to_file(self) -> None:
        """Save maze hex grid, entry/exit, and solved path to file."""
        if not self.maze:
            return

        hex_char = "0123456789ABCDEF"
        with open(self.output_file, "w", encoding="utf-8") as file_handle:
            for row in range(self.height):
                for col in range(self.width):
                    print(
                        hex_char[self.maze[row][col]],
                        end="",
                        file=file_handle
                    )
                print(file=file_handle)

            file_handle.write("\n")
            file_handle.write(f"{self.entry[1]},{self.entry[0]}\n")
            file_handle.write(f"{self.exit_coord[1]},{self.exit_coord[0]}\n")
            solve_result = self.solve_maze()
            file_handle.write(f"{solve_result}\n")
