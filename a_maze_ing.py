import glob
from pathlib import Path
import sys

_root = Path(__file__).resolve().parent
_mazegen_path = str(_root / "src" / "mazegen")
if _mazegen_path not in sys.path:
    sys.path.insert(0, _mazegen_path)

for _site_packages in glob.glob(str(_root / ".venv" / "lib" / "python*" / "site-packages")):
    if _site_packages not in sys.path:
        sys.path.insert(0, _site_packages)

from enum import IntEnum

from mlx import Mlx
from pyautogui import size

from src.mazegen.maze_generator.MazeGenerator import MazeGenerator
from src.mazegen.maze_generator.utils import get_pattern_42
from src.mazegen.maze_solver import MazeSolver
from src.mazegen.parser import parser
CONF_FILE_NAME = "config.txt"


class Directions(IntEnum):
    N = 0
    E = 1
    S = 2
    W = 3


DIR_MAZE = [-1, 0, 1, 0, -1]


def visualize_maze(maze, config, solver, steps=None):
    width, height = size()
    height -= 100
    width -= 400
    m = Mlx()
    p = m.mlx_init()
    cmodes = [
        [100, 130, 160],  # スレートブルー
        [120, 150, 170],  # ミスティブルー
        [85, 110, 130],  # デニムブルー
        [110, 150, 160],  # クラウディシアン
        [130, 140, 170],  # ラベンダーブルー
        [75, 95, 115],  # シャドウネイビー
        [145, 165, 185],  # パウダーブルー
    ]

    win = m.mlx_new_window(p, width, height, "Maze Viewer")
    img = m.mlx_new_image(p, width, height)

    img_data, bpp, line_size, endian = m.mlx_get_data_addr(img)
    bytes_per_pixel = bpp // 8

    # --- アニメーション状態 ---
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
    STEPS_PER_FRAME = max(1, rows * cols // 30)

    # 💡【修正】迷路のサイズと表示位置の計算をここに移動（初期化を共通化）
    draw_h = height - 50
    cell_size = min(width // cols, draw_h // rows)
    offset_x = (width - cols * cell_size) // 2
    offset_y = (draw_h - rows * cell_size) // 2

    cm = 0
    show_path = False

    path_cells_anim = []
    path_anim_idx = [0]
    path_anim_active = [False]
    PATH_ANIM_TOTAL_FRAMES = 10
    path_cells_per_frame = [1]

    # 壁の太さを動的に決定
    thickness = max(1, 100 // max(rows, cols))

    def clear_image():
        for y in range(height):
            idx = y * line_size
            img_data[idx : idx + width * bytes_per_pixel] = b"\x00\x00\x00\xff" * width

    def fill_cell(x0, y0, x1, y1, cmode):
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
            img_data[idx : idx + len(row_segment)] = row_segment

    def draw_wall_horizontal(x0, y, x1, cmode):
        half = thickness // 2
        fill_cell(x0, y - half, x1, y - half + thickness, cmode)

    def draw_wall_vertical(x, y0, y1, cmode):
        half = thickness // 2
        fill_cell(x - half, y0, x - half + thickness, y1, cmode)

    def draw_maze_structure(target_maze, current_cmode, current_path_cells):
        clear_image()
        pattern_cells = get_pattern_42(cols, rows)

        for y in range(rows):
            for x in range(cols):
                cell = target_maze[y][x]
                x0 = offset_x + x * cell_size
                y0 = offset_y + y * cell_size
                x1 = x0 + cell_size
                y1 = y0 + cell_size

                if (
                    (y, x) == config["ENTRY"]
                    or (y, x) == config["EXIT"]
                    or (x, y) in pattern_cells
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
        m.mlx_string_put(
            p,
            win,
            50,
            text_y,
            0xFFFFFF,
            "[C]: Recoloring [R]: Regenerate [P] Path [Esc] Exit",
        )
        m.mlx_do_sync(p)

    def render_maze(cmode, show_path, partial_path=None):
        path_cells = set()
        if partial_path is not None:
            path_cells = set(partial_path)
        elif show_path:
            path = solver.solve_maze(maze, cols, rows, config["ENTRY"], config["EXIT"])
            cy, cx = config["ENTRY"]
            path_cells.add((cy, cx))
            for d in path:
                cy += DIR_MAZE[Directions[d]]
                cx += DIR_MAZE[Directions[d] + 1]
                path_cells.add((cy, cx))

        draw_maze_structure(maze, cmode, path_cells)

    def cleanup():
        m.mlx_destroy_image(p, img)
        m.mlx_destroy_window(p, win)
        m.mlx_loop_exit(p)

    def on_key(keynum, param):
        nonlocal maze, cm, show_path, anim_initial, anim_diffs, anim_maze
        if keynum == 65307:  # Esc
            cleanup()
        elif keynum == 114:  # R
            new_maze, new_steps = MazeGenerator(config).generate_maze_steps()
            maze = new_maze
            anim_initial, anim_diffs = new_steps
            anim_maze = [row[:] for row in anim_initial]
            anim_frame[0] = 0
            anim_active[0] = True
        elif keynum == 99:  # C
            if not anim_active[0]:
                cm = (cm + 1) % 7
                render_maze(cm, show_path)
        elif keynum == 112:  # P
            if not anim_active[0] and not path_anim_active[0]:
                if show_path:
                    show_path = False
                    render_maze(cm, show_path)
                else:
                    path_str = solver.solve_maze(
                        maze, cols, rows, config["ENTRY"], config["EXIT"]
                    )
                    path_cells_anim.clear()
                    cy, cx = config["ENTRY"]
                    path_cells_anim.append((cy, cx))
                    for d in path_str:
                        cy += DIR_MAZE[Directions[d]]
                        cx += DIR_MAZE[Directions[d] + 1]
                        path_cells_anim.append((cy, cx))
                    path_anim_idx[0] = 0
                    path_cells_per_frame[0] = max(
                        1, len(path_cells_anim) // PATH_ANIM_TOTAL_FRAMES
                    )
                    path_anim_active[0] = True

    def on_loop(param):
        nonlocal show_path
        if anim_active[0]:
            for _ in range(STEPS_PER_FRAME):
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
            partial = path_cells_anim[: path_anim_idx[0] + 1]
            render_maze(cm, False, partial_path=partial)
            return

    def on_close(param):
        cleanup()

    m.mlx_loop_hook(p, on_loop, None)
    if not anim_active[0]:
        render_maze(cm, show_path)

    m.mlx_key_hook(win, on_key, None)
    m.mlx_hook(win, 33, 0, on_close, None)
    m.mlx_loop(p)

def main():
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

    solver.write_to_file()

    visualize_maze(maze, config, solver, steps=steps)


if __name__ == "__main__":
    main()
