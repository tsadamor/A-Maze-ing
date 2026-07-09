import random
from .backtracking import generate_maze_dfs, generate_maze_dfs_with_steps
from .wall_expand import gen_maze_wall_expand, gen_maze_wall_expand_with_steps


class MazeGenerator:
    def __init__(self, config: dict) -> None:
        self.width = config["WIDTH"]
        self.height = config["HEIGHT"]
        self.entry = config["ENTRY"]
        self.exit = config["EXIT"]
        self.output_file = config["OUTPUT_FILE"]
        self.perfect = config["PERFECT"]
        self.seed = config["SEED"]

    def generate_maze(self) -> list[list[int]]:
        random.seed(self.seed)

        if self.perfect:
            self.maze = generate_maze_dfs(self.width, self.height, self.entry)
        else:
            self.maze = gen_maze_wall_expand(self.width, self.height)
        return self.maze

    def generate_maze_steps(self) -> tuple[list[list[int]], list[list[list[int]]]]:
        """(完成迷路, 生成ステップリスト) を返す。アニメーション用。"""
        random.seed(self.seed)

        x = random.randint(0, 100)
        if x >= 90:
            self.maze, steps = generate_maze_dfs_with_steps(
                self.width, self.height, self.entry
            )
        else:
            self.maze, steps = gen_maze_wall_expand_with_steps(
                self.width, self.height
            )
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
