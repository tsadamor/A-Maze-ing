from parser import parser
from maze_generator.MazeGenerator import MazeGenerator
CONF_FILE_NAME = "config.txt"


def main():
    parse_result = parser(CONF_FILE_NAME)
    if not parse_result[0]:
        return

    config = parse_result[1]

    generator = MazeGenerator(config)
    generator.generate_maze()
    generator.save_maze_to_file()


if __name__ == "__main__":
    main()
