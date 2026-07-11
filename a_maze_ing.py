"""Main entrypoint for A-Maze-ing project."""

from src.mazegen.maze_generator.MazeGenerator import MazeGenerator
from src.mazegen.maze_solver import MazeSolver
from src.mazegen.parser import parser
from src.mazegen.visualizer import MazeVisualizer

CONF_FILE_NAME = "config.txt"


def main() -> None:
    """Main program entrypoint."""
    parse_result = parser(CONF_FILE_NAME)
    if not parse_result[0]:
        return

    config = parse_result[1]
    ent = config["ENTRY"]
    ext = config["EXIT"]
    wid = config["WIDTH"]
    hig = config["HEIGHT"]

    generator = MazeGenerator(config)
    maze, steps = generator.generate_maze_steps()
    generator.save_maze_to_file()

    solver = MazeSolver(maze, config["OUTPUT_FILE"], ent, ext, wid, hig)

    visualizer = MazeVisualizer(maze, config, solver, steps=steps)
    visualizer.run()


if __name__ == "__main__":
    main()
