"""Main entrypoint for A-Maze-ing project."""

from mazegen.maze_generator.MazeGenerator import MazeGenerator
from mazegen.maze_solver import MazeSolver
from mazegen.maze_visualizer import MazeVisualizer
from mazegen.parser import parser
from mazegen.utils import save_maze_to_file

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

    generator = MazeGenerator(
        width=wid,
        height=hig,
        entry=ent,
        exit_coord=ext,
        perfect=config["PERFECT"],
        seed=config.get("SEED"),
        algorithm=config.get("ALGORITHM")
    )
    maze, steps = generator.generate_maze()

    solver = MazeSolver(maze, config["OUTPUT_FILE"], ent, ext, wid, hig)
    path_str = solver.solve_maze()

    save_maze_to_file(
        maze,
        config["OUTPUT_FILE"],
        wid,
        hig,
        ent,
        ext,
        path_str,
    )

    visualizer = MazeVisualizer(maze, config, solver, steps=steps)
    visualizer.run()


if __name__ == "__main__":
    main()
