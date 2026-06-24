from .backtracking import generate_maze_dfs
from .wall_expand import gen_maze_wall_expand


class MazeGenerator:
    def __init__(self, config: dict) -> None:
        self.width = config["WIDTH"]
        self.height = config["HEIGHT"]
        self.entry = config["ENTRY"]
        self.exit = config["EXIT"]
        self.output_file = config["OUTPUT_FILE"]
        self.perfect = config["PERFECT"]

    def generate_maze(self) -> list[list[int]]:
        if self.perfect:
            self.maze = generate_maze_dfs(self.width, self.height, self.entry)
        else:
            self.maze = gen_maze_wall_expand(self.width, self.height)
        return self.maze

    def save_maze_to_file(self) -> None:
        if not self.maze:
            return

        hex_char = "0123456789ABCDEF"
        with open(self.output_file, "w", encoding="utf-8") as f:
            for h in range(self.height):
                for w in range(self.width):
                    print(hex_char[self.maze[h][w]], end="", file=f)
                print(file=f)
