"""Main entrypoint for A-Maze-ing project."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path if not present to support direct execution
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from src.mazegen.maze_generator.MazeGenerator import (  # noqa: E402
    MazeGenerator,
)
from src.mazegen.maze_solver import MazeSolver  # noqa: E402
from src.mazegen.parser import parser  # noqa: E402
from src.mazegen.visualizer import MazeVisualizer  # noqa: E402


def main() -> None:
    """Main program entrypoint handling CLI config file argument."""
    cli_parser = argparse.ArgumentParser(
        description="A-Maze-ing Maze Generator and Solver"
    )
    cli_parser.add_argument(
        "config_file", help="Path to the maze configuration file"
    )
    cli_parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Disable MLX graphical rendering window",
    )
    args = cli_parser.parse_args()

    parse_result = parser(args.config_file)
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

    if not args.no_gui:
        visualizer = MazeVisualizer(maze, config, solver, steps=steps)
        visualizer.run()


if __name__ == "__main__":
    main()
