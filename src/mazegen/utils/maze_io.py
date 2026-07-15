"""Maze I/O module for saving to file."""


def save_maze_to_file(
    maze: list[list[int]],
    output_file: str,
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_coord: tuple[int, int],
    solve_result: str,
) -> None:
    """Save maze hex grid, entry/exit, and solved path to file."""
    if not maze:
        return

    hex_char = "0123456789ABCDEF"
    with open(output_file, "w", encoding="utf-8") as file_handle:
        for row in range(height):
            for col in range(width):
                print(
                    hex_char[maze[row][col]],
                    end="",
                    file=file_handle
                )
            print(file=file_handle)

        file_handle.write("\n")
        file_handle.write(f"{entry[1]},{entry[0]}\n")
        file_handle.write(f"{exit_coord[1]},{exit_coord[0]}\n")
        file_handle.write(f"{solve_result}\n")
