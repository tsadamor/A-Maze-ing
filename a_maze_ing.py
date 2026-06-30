from enum import IntEnum

from mlx import Mlx
from pyautogui import size

from maze_generator import MazeGenerator
from maze_generator.utils import get_pattern_42
from maze_solver import MazeSolver
from parser import parser

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
    m = Mlx()
    p = m.mlx_init()
    cmodes = [
        [100, 130, 160],  # スレートブルー（グレー混じりの落ち着いた青）
        [120, 150, 170],  # ミスティブルー（霧がかったような、少し明るめの青）
        [85, 110, 130],  # デニムブルー（深みと渋みのあるインディゴ系）
        [110, 150, 160],  # クラウディシアン（やや緑がかった、くすんだトープブルー）
        [130, 140, 170],  # ラベンダーブルー（ほんのり紫を帯びた上品な青）
        [75, 95, 115],  # シャドウネイビー（暗すぎず、ニュアンスのある知的など紺）
        [145, 165, 185],  # パウダーブルー（明るく、グレイッシュで優しい上品な青）
    ]

    win = m.mlx_new_window(p, width, height, "Maze Viewer")
    img = m.mlx_new_image(p, width, height)

    img_data, bpp, line_size, endian = m.mlx_get_data_addr(img)

    cell_size = 1
    offset_x = 0
    offset_y = 0
    cm = 0
    show_path = False

    # --- アニメーション状態 (迷路生成) ---
    if steps:
        anim_initial, anim_diffs = steps
        anim_maze = [row[:] for row in anim_initial]  # 再生用作業コピー
    else:
        anim_initial = None
        anim_diffs = []
        anim_maze = None
    anim_frame = [0]  # 現在のフレームインデックス
    anim_active = [bool(steps)]
    rows = len(maze)
    cols = len(maze[0])
    STEPS_PER_FRAME = max(1, rows * cols // 20)

    # --- パスアニメーション状態 ---
    path_cells_anim = []  # パスのセル座標リスト (y, x)
    path_anim_idx = [0]  # 現在何セルまで塗ったか
    path_anim_active = [False]  # パスアニメーション中フラグ
    PATH_ANIM_TOTAL_FRAMES = 20  # パスアニメを何フレームで完了させるか (小さいほど速い)
    path_cells_per_frame = [1]  # 動的に計算される

    def put_pixel(cx, cy, cmode):
        thickness = max(1, 100 // max(rows, cols))
        offset = thickness // 2


        r, g, b = cmode[0], cmode[1], cmode[2]

        for dy in range(-offset, offset + 1):
            for dx in range(-offset, offset + 1):
                x = cx + dx
                y = cy + dy

                if not (0 <= x < width and 0 <= y < height):
                    continue

                idx = y * line_size + x * (bpp // 8)

                img_data[idx] = b
                img_data[idx + 1] = g
                img_data[idx + 2] = r
                img_data[idx + 3] = 255

    def draw_line(x0, y0, x1, y1, cmode):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        err = dx - dy

        while True:
            put_pixel(x0, y0, cmodes[cmode])

            if x0 == x1 and y0 == y1:
                break

            e2 = err * 2

            if e2 > -dy:
                err -= dy
                x0 += sx

            if e2 < dx:
                err += dx
                y0 += sy

    def clear_image():
        for y in range(height):
            for x in range(width):
                idx = y * line_size + x * (bpp // 8)

                img_data[idx] = 0
                img_data[idx + 1] = 0
                img_data[idx + 2] = 0
                img_data[idx + 3] = 255

    def fill_cell(x0, y0, x1, y1, cmode):
        """
        指定された矩形領域 (x0, y0) から (x1, y1) を指定した色で塗りつぶす
        rgb_color: [r, g, b] の配列 (例: [255, 0, 0])
        """
        r, g, b = cmodes[cmode]

        # ウィンドウの範囲外にはみ出さないようにガード（クリッピング）
        start_x = max(0, min(x0, width))
        end_x = max(0, min(x1, width))
        start_y = max(0, min(y0, height))
        end_y = max(0, min(y1, height))

        # 縦横のループでピクセルを愚直に埋める（一番高速）
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                idx = y * line_size + x * (bpp // 8)

                img_data[idx] = b
                img_data[idx + 1] = g
                img_data[idx + 2] = r
                img_data[idx + 3] = 255

    def render_maze(cmode, show_path, partial_path=None):
        """迷路を描画する。partial_path が渡されたらそのセルだけパス色で塗る。"""
        nonlocal cell_size
        nonlocal offset_x
        nonlocal offset_y

        draw_h = height - 50  # テキスト表示用に下50px確保
        cell_size = min(width // cols, draw_h // rows)

        maze_w = cols * cell_size
        maze_h = rows * cell_size

        offset_x = (width - maze_w) // 2
        offset_y = (draw_h - maze_h) // 2

        clear_image()

        pattern_cells = get_pattern_42(cols, rows)
        path_cells = []
        if partial_path is not None:
            path_cells = partial_path
        elif show_path:
            path = solver.solve_maze(
                maze,
                cols,
                rows,
                config["ENTRY"],
                config["EXIT"],
            )
            cy, cx = config["ENTRY"]
            path_cells.append((cy, cx))
            for d in path:
                cy += DIR_MAZE[Directions[d]]
                cx += DIR_MAZE[Directions[d] + 1]
                path_cells.append((cy, cx))

        for y in range(rows):
            for x in range(cols):
                cell = maze[y][x]

                x0 = offset_x + x * cell_size
                y0 = offset_y + y * cell_size

                x1 = x0 + cell_size
                y1 = y0 + cell_size

                if (
                    (y, x) == config["ENTRY"]
                    or (y, x) == config["EXIT"]
                    or (x, y) in pattern_cells
                ):
                    print(y, x)
                    fill_cell(x0, y0, x1, y1, (cmode + 1) % 7)
                elif (y, x) in path_cells:
                    fill_cell(x0, y0, x1, y1, (cmode + 2) % 7)
                if cell & 1 << Directions.N:
                    draw_line(x0, y0, x1, y0, cmode)

                if cell & 1 << Directions.E:
                    draw_line(x1, y0, x1, y1, cmode)

                if cell & 1 << Directions.S:
                    draw_line(x0, y1, x1, y1, cmode)

                if cell & 1 << Directions.W:
                    draw_line(x0, y0, x0, y1, cmode)

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

    def cleanup():
        m.mlx_destroy_image(p, img)
        m.mlx_destroy_window(p, win)
        m.mlx_loop_exit(p)

    def on_key(keynum, param):
        nonlocal maze
        nonlocal cm
        nonlocal show_path
        nonlocal anim_initial, anim_diffs, anim_maze

        print(f"{keynum} key pressed")

        if keynum == 65307:  # Esc
            cleanup()

        elif keynum == 114:  # R: 再生成（アニメーション付き）
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
                    # パス非表示に戻す
                    show_path = False
                    render_maze(cm, show_path)
                else:
                    # パスアニメーション開始
                    path_str = solver.solve_maze(
                        maze,
                        cols,
                        rows,
                        config["ENTRY"],
                        config["EXIT"],
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
        """mlx_loop_hook コールバック。迷路生成アニメ・パスアニメの両方を処理。"""
        nonlocal show_path

        # --- 迷路生成アニメーション ---
        if anim_active[0]:
            # STEPS_PER_FRAME 分の差分を anim_maze に適用
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

            # anim_maze を描画
            draw_h = height - 50
            cs = min(width // cols, draw_h // rows)
            ox = (width - cols * cs) // 2
            oy = (draw_h - rows * cs) // 2

            clear_image()

            for ry in range(rows):
                for rx in range(cols):
                    cell = anim_maze[ry][rx]
                    x0 = ox + rx * cs
                    y0 = oy + ry * cs
                    x1 = x0 + cs
                    y1 = y0 + cs

                    if cell & 1 << Directions.N:
                        draw_line(x0, y0, x1, y0, cm)
                    if cell & 1 << Directions.E:
                        draw_line(x1, y0, x1, y1, cm)
                    if cell & 1 << Directions.S:
                        draw_line(x0, y1, x1, y1, cm)
                    if cell & 1 << Directions.W:
                        draw_line(x0, y0, x0, y1, cm)

            m.mlx_put_image_to_window(p, win, img, 0, 0)
            m.mlx_do_sync(p)
            return

        # --- パスアニメーション ---
        if path_anim_active[0]:
            path_anim_idx[0] += path_cells_per_frame[0]

            if path_anim_idx[0] >= len(path_cells_anim):
                # 完了: show_path=True で通常描画に移行
                path_anim_active[0] = False
                show_path = True
                render_maze(cm, show_path)
                return

            # 現在まで塗ったセルのスライスで再描画
            partial = path_cells_anim[: path_anim_idx[0] + 1]
            render_maze(cm, False, partial_path=partial)
            return

    def on_close(param):
        cleanup()

    # アニメーションがあれば loop_hook を常に登録しておく
    m.mlx_loop_hook(p, on_loop, None)

    # アニメーションがない場合は通常の完成迷路を描画して開始
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
