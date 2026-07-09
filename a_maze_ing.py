"""Main entrypoint for A-Maze-ing project."""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path if not present to support direct execution
_root = Path(__file__).resolve().parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from typing import Any  # noqa: E402

from src.mazegen.maze_generator.MazeGenerator import (  # noqa: E402
    MazeGenerator,
)
from src.mazegen.maze_generator.utils import (  # noqa: E402
    DIR_MAZE,
    Directions,
    get_pattern_42,
)
from src.mazegen.maze_solver import MazeSolver  # noqa: E402
from src.mazegen.parser import parser  # noqa: E402


def visualize_maze(
    maze: list[list[int]],
    config: dict[str, Any],
    solver: MazeSolver,
    steps: Any = None,
) -> None:
    """Render maze using MLX graphical window.

    Args:
        maze (list[list[int]]): 2D list of wall masks representing the maze.
        config (dict[str, Any]): Maze configuration dictionary.
        solver (MazeSolver): The solver instance to find paths.
        steps (Any, optional): Step history for animation. Defaults to None.
    """
    try:
        from mlx import Mlx
        from pyautogui import size
    except Exception:
        print(
            "Graphical visualization is not available (MLX/PyAutoGUI missing "
            "or headless environment)."
        )
        return

    try:
        width, height = size()
        height -= 100
        width -= 400
        m = Mlx()
        p = m.mlx_init()
        if p is None:
            raise RuntimeError("MLX initialization failed")
    except Exception:
        print(
            "Graphical visualization initialization failed "
            "(MLX initialization failed)."
        )
        return

    cmodes = [
        [100, 130, 160],
        [120, 150, 170],
        [85, 110, 130],
        [110, 150, 160],
        [130, 140, 170],
        [75, 95, 115],
        [145, 165, 185],
    ]

    win = m.mlx_new_window(p, width, height, "Maze Viewer")
    img = m.mlx_new_image(p, width, height)

    img_data, bpp, line_size, endian = m.mlx_get_data_addr(img)
    bytes_per_pixel = bpp // 8

    if steps:
        anim_initial, anim_diffs = steps
        anim_maze = [row[:] for row in anim_initial]
    else:
        anim_initial = None
        anim_diffs = []
        anim_maze = None
    anim_frame = [0]
    anim_active = [bool(steps)]
    rows = len(maze)
    cols = len(maze[0])
    steps_per_frame = max(1, rows * cols // 30)

    draw_h = height - 50
    cell_size = min(width // cols, draw_h // rows)
    offset_x = (width - cols * cell_size) // 2
    offset_y = (draw_h - rows * cell_size) // 2

    cm = 0
    show_path = False
    player_pos = list(config["ENTRY"])

    path_cells_anim: list[tuple[int, int]] = []
    path_anim_idx = [0]
    path_anim_active = [False]
    path_anim_total = 10
    path_cells_per_frame = [1]

    thickness = max(1, 100 // max(rows, cols))

    def clear_image() -> None:
        """Clear the window image to black."""
        row_blank = b"\x00\x00\x00\xff" * width
        for y in range(height):
            idx = y * line_size
            img_data[idx:idx + width * bytes_per_pixel] = row_blank

    def fill_cell(x0: int, y0: int, x1: int, y1: int, cmode: int) -> None:
        """Fill a rectangular region of the image with a color.

        Args:
            x0 (int): Start X coordinate.
            y0 (int): Start Y coordinate.
            x1 (int): End X coordinate.
            y1 (int): End Y coordinate.
            cmode (int): Color mode index.
        """
        r, g, b = cmodes[cmode]
        start_x = max(0, min(x0, width))
        end_x = max(0, min(x1, width))
        start_y = max(0, min(y0, height))
        end_y = max(0, min(y1, height))

        if start_x >= end_x or start_y >= end_y:
            return

        color_bytes = bytes([b, g, r, 255])
        row_segment = color_bytes * (end_x - start_x)

        for y in range(start_y, end_y):
            idx = y * line_size + start_x * bytes_per_pixel
            img_data[idx:idx + len(row_segment)] = row_segment

    def draw_wall_horizontal(x0: int, y: int, x1: int, cmode: int) -> None:
        """Draw a horizontal wall line on the image.

        Args:
            x0 (int): Start X coordinate.
            y (int): Y coordinate of the wall.
            x1 (int): End X coordinate.
            cmode (int): Color mode index.
        """
        half = thickness // 2
        fill_cell(x0, y - half, x1, y - half + thickness, cmode)

    def draw_wall_vertical(x: int, y0: int, y1: int, cmode: int) -> None:
        """Draw a vertical wall line on the image.

        Args:
            x (int): X coordinate of the wall.
            y0 (int): Start Y coordinate.
            y1 (int): End Y coordinate.
            cmode (int): Color mode index.
        """
        half = thickness // 2
        fill_cell(x - half, y0, x - half + thickness, y1, cmode)

    def draw_maze_structure(
        target_maze: list[list[int]],
        current_cmode: int,
        current_path_cells: set[tuple[int, int]],
    ) -> None:
        """Draw the cells and walls of the maze structure.

        Args:
            target_maze (list[list[int]]): 2D list of wall masks.
            current_cmode (int): Active color mode.
            current_path_cells (set[tuple[int, int]]): Set of (row, col)
                cells in path.
        """
        clear_image()
        pattern_cells = get_pattern_42(cols, rows)

        for y in range(rows):
            for x in range(cols):
                cell = target_maze[y][x]
                x0 = offset_x + x * cell_size
                y0 = offset_y + y * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size

                if (y, x) == tuple(player_pos):
                    fill_cell(x0, y0, x1, y1, (current_cmode + 3) % 7)
                elif (
                    (y, x) == config["ENTRY"]
                    or (y, x) == config["EXIT"]
                    or (y, x) in pattern_cells
                ):
                    fill_cell(x0, y0, x1, y1, (current_cmode + 1) % 7)
                elif (y, x) in current_path_cells:
                    fill_cell(x0, y0, x1, y1, (current_cmode + 2) % 7)

                if cell & (1 << Directions.N):
                    draw_wall_horizontal(x0, y0, x1, current_cmode)
                if cell & (1 << Directions.E):
                    draw_wall_vertical(x1, y0, y1, current_cmode)
                if cell & (1 << Directions.S):
                    draw_wall_horizontal(x0, y1, x1, current_cmode)
                if cell & (1 << Directions.W):
                    draw_wall_vertical(x0, y0, y1, current_cmode)

        m.mlx_put_image_to_window(p, win, img, 0, 0)
        text_y = height - 40
        if tuple(player_pos) == config["EXIT"]:
            msg = (
                "*** CONGRATULATIONS! You reached the Exit! *** [R] to Restart"
            )
            m.mlx_string_put(p, win, 50, text_y, 0x00FF00, msg)
        else:
            msg = (
                "[C]: Color [R]: Regenerate [P]: Path "
                "[Arrows/WASD]: Move [Esc]: Exit"
            )
            m.mlx_string_put(p, win, 50, text_y, 0xFFFFFF, msg)
        m.mlx_do_sync(p)

    def render_maze(
        cmode: int,
        show_path: bool,
        partial_path: list[tuple[int, int]] | None = None,
    ) -> None:
        """Render the complete maze representation, including solver path.

        Args:
            cmode (int): Color mode index.
            show_path (bool): Whether to show the completed solver path.
            partial_path (list[tuple[int, int]] | None, optional): Partial
                path for animation. Defaults to None.
        """
        path_cells = set()
        if partial_path is not None:
            path_cells = set(partial_path)
        elif show_path:
            path = solver.solve_maze()
            cy, cx = config["ENTRY"]
            path_cells.add((cy, cx))
            for d in path:
                cy += DIR_MAZE[Directions[d]]
                cx += DIR_MAZE[Directions[d] + 1]
                path_cells.add((cy, cx))

        draw_maze_structure(maze, cmode, path_cells)

    def cleanup() -> None:
        """Destroy window, image, and exit loop to release MLX resources."""
        m.mlx_destroy_image(p, img)
        m.mlx_destroy_window(p, win)
        m.mlx_loop_exit(p)

    def on_key(keynum: int, param: Any) -> None:
        """Keyboard input callback for MLX window interactions.

        Args:
            keynum (int): The pressed key code.
            param (Any): Additional parameter passed by MLX.
        """
        nonlocal maze, cm, show_path, anim_initial, anim_diffs, anim_maze
        if keynum == 65307:
            cleanup()
        elif keynum == 114:
            gen = MazeGenerator(config)
            new_maze, new_steps = gen.generate_maze_steps()
            maze = new_maze
            gen.save_maze_to_file()
            anim_initial, anim_diffs = new_steps
            if anim_initial:
                anim_maze = [row[:] for row in anim_initial]
            anim_frame[0] = 0
            anim_active[0] = True
            player_pos[0], player_pos[1] = config["ENTRY"]
        elif keynum == 99:
            if not anim_active[0]:
                cm = (cm + 1) % 7
                render_maze(cm, show_path)
        elif keynum == 112:
            if not anim_active[0] and not path_anim_active[0]:
                if show_path:
                    show_path = False
                    render_maze(cm, show_path)
                else:
                    path_str = solver.solve_maze()
                    path_cells_anim.clear()
                    cy, cx = config["ENTRY"]
                    path_cells_anim.append((cy, cx))
                    for d in path_str:
                        cy += DIR_MAZE[Directions[d]]
                        cx += DIR_MAZE[Directions[d] + 1]
                        path_cells_anim.append((cy, cx))
                    path_anim_idx[0] = 0
                    path_cells_per_frame[0] = max(
                        1, len(path_cells_anim) // path_anim_total
                    )
                    path_anim_active[0] = True

        move_map = {
            65362: (Directions.N, -1, 0),  # Up
            119: (Directions.N, -1, 0),    # W
            65364: (Directions.S, 1, 0),   # Down
            115: (Directions.S, 1, 0),    # S
            65361: (Directions.W, 0, -1),  # Left
            97: (Directions.W, 0, -1),     # A
            65363: (Directions.E, 0, 1),   # Right
            100: (Directions.E, 0, 1),     # D
        }
        if keynum in move_map:
            if not anim_active[0] and not path_anim_active[0]:
                d_dir, dr, dc = move_map[keynum]
                r, c = player_pos[0], player_pos[1]
                if not (maze[r][c] & (1 << d_dir)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        player_pos[0], player_pos[1] = nr, nc
                        render_maze(cm, show_path)

    def on_loop(param: Any) -> None:
        """Frame updates hook callback for animations.

        Args:
            param (Any): Additional parameter passed by MLX.
        """
        nonlocal show_path
        if anim_active[0] and anim_maze:
            for _ in range(steps_per_frame):
                if anim_frame[0] >= len(anim_diffs):
                    break
                for dy, dx, val in anim_diffs[anim_frame[0]]:
                    anim_maze[dy][dx] = val
                anim_frame[0] += 1

            if anim_frame[0] >= len(anim_diffs):
                anim_active[0] = False
                render_maze(cm, show_path)
                return

            draw_maze_structure(anim_maze, cm, set())
            return

        if path_anim_active[0]:
            path_anim_idx[0] += path_cells_per_frame[0]
            if path_anim_idx[0] >= len(path_cells_anim):
                path_anim_active[0] = False
                show_path = True
                render_maze(cm, show_path)
                return
            partial = path_cells_anim[:path_anim_idx[0] + 1]
            render_maze(cm, False, partial_path=partial)
            return

    def on_close(param: Any) -> None:
        """Window close event callback.

        Args:
            param (Any): Additional parameter passed by MLX.
        """
        cleanup()

    m.mlx_loop_hook(p, on_loop, None)
    if not anim_active[0]:
        render_maze(cm, show_path)

    m.mlx_key_hook(win, on_key, None)
    m.mlx_hook(win, 33, 0, on_close, None)
    m.mlx_loop(p)


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
        visualize_maze(maze, config, solver, steps=steps)


if __name__ == "__main__":
    main()
