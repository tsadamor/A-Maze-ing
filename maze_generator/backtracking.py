import random
from utils.patterns import get_pattern_42


def generate_maze_dfs(
        width: int, height: int,
        entry: tuple[int, int]
        ) -> list[list[int]]:
    grid = [[15 for _ in range(width)] for _ in range(height)]
    directions = [
            (0, 0, -1),
            (1, 1, 0),
            (2, 0, 1),
            (3, -1, 0)
            ]
    stack = [entry]
    visited = {entry}
    blocked_area = get_pattern_42(width, height)

    if blocked_area:
        visited.update(blocked_area)

    while stack:
        current = stack[-1]
        x, y = current
        valid_neighbors = []

        for bit_pos, dx, dy in directions:
            nx = x + dx
            ny = y + dy
            if (
                nx >= 0 and nx < width
                and ny >= 0 and ny < height
                and (nx, ny) not in visited
            ):
                valid_neighbors.append((bit_pos, nx, ny))
        if valid_neighbors:
            new = random.choice(valid_neighbors)
        else:
            stack.pop()
            continue

        bit_pos, nx, ny = new
        opposit_bit_pos = (bit_pos + 2) % 4
        grid[y][x] ^= (1 << bit_pos)
        grid[ny][nx] ^= (1 << opposit_bit_pos)

        stack.append((nx, ny))
        visited.add((nx, ny))

    return grid


def print_ascii_maze(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_coord: tuple[int, int]
) -> None:
    """
    grid データを読み込み、壁を『#』、通路を『  』で描きつつ、
    入口を『ST』、出口を『ED』としてターミナルに出力する関数
    """
    if not grid:
        return

    height = len(grid)
    width = len(grid[0])

    # 1. 「2倍 + 1」のサイズで、すべて壁（"##"）で埋まったキャンバスを作成
    canvas_height = 2 * height + 1
    canvas_width = 2 * width + 1
    canvas = [["##" for _ in range(canvas_width)] for _ in range(canvas_height)]

    # 2. 元の迷路を1マスずつチェックしてキャンバスを削る
    for y in range(height):
        for x in range(width):
            cy = 2 * y + 1
            cx = 2 * x + 1

            cell_value = grid[y][x]

            if cell_value == 15:
                # 中心、上下左右、さらに「斜めの角」もすべて含めて 3x3 を ██ で塗りつぶ
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        canvas[cy + dy][cx + dx] = "██"
                continue           # 中心を通路（空白）にする
            canvas[cy][cx] = "  "

           

            # 各方向のビットをチェックして壁をぶち抜く
            if not (cell_value & (1 << 0)):  # 北
                canvas[cy - 1][cx] = "  "
            if not (cell_value & (1 << 1)):  # 東
                canvas[cy][cx + 1] = "  "
            if not (cell_value & (1 << 2)):  # 南
                canvas[cy + 1][cx] = "  "
            if not (cell_value & (1 << 3)):  # 西
                canvas[cy][cx - 1] = "  "

    # 3. 【追加】入口と出口の座標に目印（2文字）を上書きする
    entry_x, entry_y = entry
    exit_x, exit_y = exit_coord

    canvas[2 * entry_y + 1][2 * entry_x + 1] = "ST"  # Start (入口)
    canvas[2 * exit_y + 1][2 * exit_x + 1] = "ED"  # End (出口)

    # 4. 画面に出力
    for row in canvas:
        print("".join(row))


if __name__ == "__main__":
    import sys

    width = 10
    height = 11
    entry = (0, 0)
    # 出口を右下のマスに設定
    exit_coord = (width - 1, height - 1)

    if len(sys.argv) == 3:
        width = int(sys.argv[1])
        height = int(sys.argv[2])
        # 引数でサイズが変わった場合も、自動で右下にゴールを設定
        exit_coord = (width - 1, height - 1)

    print(f"--- Generating Maze ({width} x {height}) ---")
    generated_grid = generate_maze_dfs(width, height, entry)

    print("\n--- Visualized ASCII Maze ---")
    # 引数に入口と出口を足して呼び出す
    print_ascii_maze(generated_grid, entry, exit_coord)
