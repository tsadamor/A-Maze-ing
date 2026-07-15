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
    from mazegen.maze_generator import MazeGenerator

    # Create a 20x15 perfect maze with a seed
    generator = MazeGenerator(
        width=20,
        height=15,
        entry=(0, 0),
        exit_coord=(14, 19),
        perfect=True,
        seed=42
    )

    # Generate the grid structure
    grid = generator.generate_maze()

    # Access the generated grid cell (row 0, col 0)
    start_cell_mask = grid[0][0]

    # Access the solution (Now requires MazeSolver separately)
    # ...
"""

import random
import sys
from collections.abc import Callable
from typing import Any

from .backtracking import generate_maze_dfs
from .braided import generate_maze_pacman
from .wall_expand import gen_maze_wall_expand

# Mapping for extensible algorithm registration
MazeResult = tuple[list[list[int]], tuple[list[list[int]], list[list[Any]]]]
Algorithm = Callable[[int, int, tuple[int, int]], MazeResult]

_ALGORITHMS: dict[str, Algorithm] = {
    "dfs": generate_maze_dfs,
    "wall_expand": gen_maze_wall_expand,
    "pacman": generate_maze_pacman,
}
_ALGORITHM_NAMES: dict[int, str] = {
    0: "dfs",
    1: "wall_expand",
    2: "pacman",
}


class MazeGenerator:
    """A configurable maze generator for perfect and braided mazes.

    Instantiates a generator that can create standard perfect mazes (using
    DFS or Wilson's Wall Expansion) or multi-route playable boards containing
    loops.

    To instantiate, provide explicit maze parameters such as width and height.

    Attributes:
        width (int): Maze width in cells (number of columns).
        height (int): Maze height in cells (number of rows).
        entry (tuple[int, int]): Entry coordinate as (row, col).
        exit_coord (tuple[int, int]): Exit coordinate as (row, col).
        perfect (bool): True to generate a perfect maze (no loops, single
            path), False to generate a braided playable maze.
        seed (int | None): Optional random seed for deterministic generation.
        maze (list[list[int]]): 2D list of integer wall masks. Each cell is
            represented by a 4-bit integer mask indicating closed walls:
                - Bit 0 (val 1): North wall is closed
                - Bit 1 (val 2): East wall is closed
                - Bit 2 (val 4): South wall is closed
                - Bit 3 (val 8): West wall is closed
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_coord: tuple[int, int],
        perfect: bool = True,
        seed: int | None = None,
    ) -> None:
        """Initialize MazeGenerator with explicit parameters.

        Args:
            width (int): Maze width in cells.
            height (int): Maze height in cells.
            entry (tuple[int, int]): Entry coordinate as (row, col).
            exit_coord (tuple[int, int]): Exit coordinate as (row, col).
            perfect (bool): Whether to generate a perfect maze.
            seed (int | None): Optional random seed for reproducibility.
        """
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_coord = exit_coord
        self.perfect = perfect
        self.seed = seed

        self.maze: list[list[int]] = []

    def _check_pattern_42_size(self) -> None:
        """Warn if maze size is too small to render the '42' pattern."""
        if self.width < 9 or self.height < 7:
            print(
                "Warning: Maze size too small to display '42' pattern.",
                file=sys.stderr,
            )

    def generate_maze(self) -> MazeResult:
        """Generate maze structure based on configuration.

        Returns:
            list[list[int]]: 2D list of integer wall masks.
        """
        self._check_pattern_42_size()
        if self.seed is not None:
            random.seed(self.seed)

        algo = _ALGORITHM_NAMES[random.randint(0, 1)]
        if not self.perfect:
            algo = "pacman"
        generator = _ALGORITHMS.get(algo, generate_maze_pacman)
        result = generator(self.width, self.height, self.entry)
        self.maze = result[0]
        return result

    def get_maze(self) -> list[list[int]]:
        """Access generated maze structure, generating if needed.

        Returns:
            list[list[int]]: 2D list of integer wall masks.
        """
        if not self.maze:
            self.generate_maze()
        return self.maze
