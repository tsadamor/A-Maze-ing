import random
from typing import Any

from .backtracking import generate_maze_dfs, generate_maze_dfs_with_steps
from .braid import braid_maze

Maze = list[list[int]]
StepDiff = list[tuple[int, int, int]]
AnimationSteps = tuple[Maze, list[StepDiff]]


class MazeGenerator:
    def __init__(self, config: dict[str, Any]) -> None:
        self.width = config["WIDTH"]
        self.height = config["HEIGHT"]
        self.entry = config["ENTRY"]
        self.exit = config["EXIT"]
        self.output_file = config["OUTPUT_FILE"]
        self.perfect = config["PERFECT"]
        self.seed = config["SEED"]
        self.maze: Maze = []

    def _entry_for_generator(self) -> tuple[int, int]:
        """Return entry as (x, y), the coordinate order used by generators."""
        return (self.entry[1], self.entry[0])

    def _protected_corridors(self) -> set[tuple[int, int]]:
        """Return non-perfect cells that must stay open for gameplay."""
        return {
            self.entry,
            self.exit,
            (0, 0),
            (0, self.width - 1),
            (self.height - 1, 0),
            (self.height - 1, self.width - 1),
            (self.height // 2, self.width // 2),
        }

    def generate_maze(self) -> Maze:
        random.seed(self.seed)

        if self.perfect:
            self.maze = generate_maze_dfs(
                self.width, self.height, self._entry_for_generator()
            )
        else:
            self.maze = generate_maze_dfs(
                self.width, self.height, self._entry_for_generator()
            )
            self.maze, _ = braid_maze(
                self.maze,
                self.width,
                self.height,
                self._protected_corridors(),
            )
        return self.maze

    def generate_maze_steps(self) -> tuple[Maze, AnimationSteps]:
        """(完成迷路, 生成ステップリスト) を返す。アニメーション用。"""
        random.seed(self.seed)

        if self.perfect:
            self.maze, steps = generate_maze_dfs_with_steps(
                self.width, self.height, self._entry_for_generator()
            )
        else:
            self.maze, steps = generate_maze_dfs_with_steps(
                self.width, self.height, self._entry_for_generator()
            )
            initial, diffs = steps
            self.maze, braid_diffs = braid_maze(
                self.maze,
                self.width,
                self.height,
                self._protected_corridors(),
            )
            diffs.extend(braid_diffs)
            steps = (initial, diffs)
        return self.maze, steps

    def save_maze_to_file(self) -> None:
        if not self.maze:
            return

        hex_char = "0123456789ABCDEF"
        with open(self.output_file, "w", encoding="utf-8") as f:
            for h in range(self.height):
                for w in range(self.width):
                    print(hex_char[self.maze[h][w]], end="", file=f)
                print(file=f)
