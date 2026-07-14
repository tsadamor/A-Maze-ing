"""Maze visualizer module using MLX."""

from typing import Any

from mazegen.maze_generator.MazeGenerator import MazeGenerator
from mazegen.maze_solver import MazeSolver
from mazegen.utils import (
    DIR_MAZE,
    Directions,
    get_pattern_42,
    save_maze_to_file,
)


class MazeVisualizer:
    """Renders and animates maze generation and solving using MLX."""

    def __init__(
        self,
        maze: list[list[int]],
        config: dict[str, Any],
        solver: MazeSolver,
        steps: Any = None,
    ) -> None:
        """Initialize the maze visualizer.

        Args:
            maze (list[list[int]]): 2D list of wall masks for the maze.
            config (dict[str, Any]): Maze configuration dictionary.
            solver (MazeSolver): The solver instance to find paths.
            steps (Any, optional): Step history for animation. Defaults None.
        """
        self.maze = maze
        self.config = config
        self.solver = solver

        try:
            from mlx import Mlx
        except Exception:
            print(
                "Graphical visualization is not available (MLX/PyAutoGUI "
                "missing or headless environment)."
            )
            self.available = False
            return

        try:
            self.m = Mlx()
            self.p = self.m.mlx_init()
            if self.p is None:
                raise RuntimeError("MLX initialization failed")
        except Exception:
            print(
                "Graphical visualization initialization failed "
                "(MLX initialization failed)."
            )
            self.available = False
            return

        self.available = True
        # Each theme defines colors for walls, landmarks, and the solved path.
        self.cmodes = [
            ((126, 249, 255), (255, 92, 138), (145, 255, 174)),  # Cyan & Pink theme
            ((89, 196, 255), (255, 204, 92), (77, 255, 218)),    # Sky blue & Yellow theme
            ((255, 167, 92), (255, 80, 120), (255, 231, 128)),   # Orange & Pink theme
            ((255, 183, 213), (255, 92, 147), (204, 178, 255)),  # Pink & Lavender theme
            ((112, 224, 151), (255, 194, 92), (173, 255, 108)),  # Green & Orange theme
            ((0, 240, 255), (255, 45, 190), (247, 255, 0)),      # Neon theme
            ((190, 168, 255), (255, 145, 200), (132, 224, 255)), # Purple & Pink theme
            ((255, 112, 67), (255, 213, 79), (255, 171, 145)),   # Coral & Yellow theme
            ((185, 230, 255), (110, 168, 255), (225, 255, 255)), # Winter blue theme
            ((128, 255, 214), (255, 148, 180), (211, 255, 140)), # Aqua & Lime theme
            ((165, 148, 255), (255, 196, 82), (104, 214, 255)),  # Violet & Gold theme
            ((224, 230, 238), (255, 105, 105), (112, 224, 178)), # Grey & Red theme
        ]
        self.cm = 0
        self.show_path = False

        _, width, height = self.m.mlx_get_screen_size(self.p)
        self.height = height - 100
        self.width = width - 400
        self.win = self.m.mlx_new_window(
            self.p, self.width, self.height, "Maze Viewer"
        )
        self.img = self.m.mlx_new_image(self.p, self.width, self.height)

        img_data, bpp, line_size, _ = self.m.mlx_get_data_addr(self.img)
        self.img_data = img_data
        self.line_size = line_size
        self.bytes_per_pixel = bpp // 8

        if steps:
            self.anim_initial, self.anim_diffs = steps
            self.anim_maze: list[list[int]] | None = [
                row[:] for row in self.anim_initial
            ]
        else:
            self.anim_initial = None
            self.anim_diffs = []
            self.anim_maze = None

        self.anim_frame = 0
        self.anim_active = bool(steps)
        self.rows = len(self.maze)
        self.cols = len(self.maze[0])
        self.steps_per_frame = max(1, self.rows * self.cols // 30)

        self.pattern_cells = get_pattern_42(self.cols, self.rows)
        self.solved_path_cells: set[tuple[int, int]] = set()

        self.draw_h = self.height - 50
        self.cell_size = min(
            self.width // self.cols, self.draw_h // self.rows
        )
        self.offset_x = (self.width - self.cols * self.cell_size) // 2
        self.offset_y = (self.draw_h - self.rows * self.cell_size) // 2
        self.thickness = max(1, 100 // max(self.rows, self.cols))

        self.path_cells_anim: list[tuple[int, int]] = []
        self.path_anim_idx = 0
        self.path_anim_active = False
        self.path_anim_total = 10
        self.path_cells_per_frame = 1

        self._update_solved_path()

    def _update_solved_path(self) -> None:
        """Update the set of path cells from the solved path string.

        Returns:
            None
        """
        self.solved_path_cells.clear()
        path = self.solver.solve_maze()
        cy, cx = self.config["ENTRY"]
        self.solved_path_cells.add((cy, cx))
        for d in path:
            cy += DIR_MAZE[Directions[d]]
            cx += DIR_MAZE[Directions[d] + 1]
            self.solved_path_cells.add((cy, cx))

    def _clear_image(self) -> None:
        """Clear the entire image buffer with a black background.

        Returns:
            None
        """
        row_blank = b"\x00\x00\x00\xff" * self.width
        for y in range(self.height):
            idx = y * self.line_size
            self.img_data[
                idx:idx + self.width * self.bytes_per_pixel
            ] = row_blank

    def _fill_cell(
        self,
        x0: int,
        y0: int,
        x1: int,
        y1: int,
        color: tuple[int, int, int],
    ) -> None:
        """Draw a filled rectangle into the image buffer.

        Args:
            x0 (int): Start X coordinate.
            y0 (int): Start Y coordinate.
            x1 (int): End X coordinate.
            y1 (int): End Y coordinate.
            color (tuple[int, int, int]): RGB color tuple to fill with.

        Returns:
            None
        """
        r, g, b = color
        start_x = max(0, min(x0, self.width))
        end_x = max(0, min(x1, self.width))
        start_y = max(0, min(y0, self.height))
        end_y = max(0, min(y1, self.height))

        if start_x >= end_x or start_y >= end_y:
            return

        color_bytes = bytes([b, g, r, 255])
        row_segment = color_bytes * (end_x - start_x)

        for y in range(start_y, end_y):
            idx = y * self.line_size + start_x * self.bytes_per_pixel
            self.img_data[idx:idx + len(row_segment)] = row_segment

    def _draw_wall_horizontal(
        self, x0: int, y: int, x1: int, cmode: int
    ) -> None:
        """Draw a horizontal wall centered at the specified Y coordinate.

        Args:
            x0 (int): Start X coordinate.
            y (int): Y coordinate (center of the wall).
            x1 (int): End X coordinate.
            cmode (int): Color mode index.

        Returns:
            None
        """
        half = self.thickness // 2
        wall_color = self.cmodes[cmode][0]
        self._fill_cell(
            x0, y - half, x1, y - half + self.thickness, wall_color
        )

    def _draw_wall_vertical(
        self, x: int, y0: int, y1: int, cmode: int
    ) -> None:
        """Draw a vertical wall centered at the specified X coordinate.

        Args:
            x (int): X coordinate (center of the wall).
            y0 (int): Start Y coordinate.
            y1 (int): End Y coordinate.
            cmode (int): Color mode index.

        Returns:
            None
        """
        half = self.thickness // 2
        wall_color = self.cmodes[cmode][0]
        self._fill_cell(
            x - half, y0, x - half + self.thickness, y1, wall_color
        )

    def _draw_maze_structure(
        self,
        target_maze: list[list[int]],
        current_cmode: int,
        current_path_cells: set[tuple[int, int]],
    ) -> None:
        """Core rendering logic to draw the maze grid, walls, and paths.

        Args:
            target_maze (list[list[int]]): Maze grid to render.
            current_cmode (int): Color mode index.
            current_path_cells (set[tuple[int, int]]): Path cells to highlight.

        Returns:
            None
        """
        self._clear_image()
        _, landmark_color, path_color = self.cmodes[current_cmode]

        for y in range(self.rows):
            for x in range(self.cols):
                cell = target_maze[y][x]
                x0 = self.offset_x + x * self.cell_size
                y0 = self.offset_y + y * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size

                if (
                    (y, x) == self.config["ENTRY"]
                    or (y, x) == self.config["EXIT"]
                    or (y, x) in self.pattern_cells
                ):
                    self._fill_cell(
                        x0, y0, x1, y1, landmark_color
                    )
                elif (y, x) in current_path_cells:
                    self._fill_cell(
                        x0, y0, x1, y1, path_color
                    )

                if cell & (1 << Directions.N):
                    self._draw_wall_horizontal(x0, y0, x1, current_cmode)
                if cell & (1 << Directions.E):
                    self._draw_wall_vertical(x1, y0, y1, current_cmode)
                if cell & (1 << Directions.S):
                    self._draw_wall_horizontal(x0, y1, x1, current_cmode)
                if cell & (1 << Directions.W):
                    self._draw_wall_vertical(x0, y0, y1, current_cmode)

        self.m.mlx_put_image_to_window(self.p, self.win, self.img, 0, 0)
        text_y = self.height - 40
        msg = "[C]: Color [R]: Regenerate [P]: Path [Esc]: Exit"
        self.m.mlx_string_put(self.p, self.win, 50, text_y, 0xFFFFFF, msg)
        self.m.mlx_do_sync(self.p)

    def _render_maze(
        self,
        cmode: int,
        show_path: bool,
        partial_path: list[tuple[int, int]] | None = None,
    ) -> None:
        """Determine path visibility and trigger maze rendering.

        Args:
            cmode (int): Color mode index.
            show_path (bool): True to show the full solved path.
            partial_path (list[tuple[int, int]] | None): Optional list of path
                coordinates for animation frames.

        Returns:
            None
        """
        path_cells = set()
        if partial_path is not None:
            path_cells = set(partial_path)
        elif show_path:
            path_cells = self.solved_path_cells

        self._draw_maze_structure(self.maze, cmode, path_cells)

    def _cleanup(self) -> None:
        """Free MLX resources and exit the application.

        Returns:
            None
        """
        self.m.mlx_destroy_image(self.p, self.img)
        self.m.mlx_destroy_window(self.p, self.win)
        self.m.mlx_loop_exit(self.p)

    def _on_key(self, keynum: int, param: Any) -> None:
        """Handle keyboard events during the MLX event loop.

        Args:
            keynum (int): The key code pressed.
            param (Any): Unused MLX parameter.

        Returns:
            None
        """
        if keynum == 65307:  # Esc key: Exit application
            self._cleanup()
        elif keynum == 114:  # 'r' key: Regenerate maze
            gen = MazeGenerator(
                width=self.config["WIDTH"],
                height=self.config["HEIGHT"],
                entry=self.config["ENTRY"],
                exit_coord=self.config["EXIT"],
                perfect=self.config["PERFECT"],
                seed=self.config.get("SEED"),
                algorithm=self.config.get("ALGORITHM")
            )
            new_maze, new_steps = gen.generate_maze()
            self.maze = new_maze
            self.anim_initial, self.anim_diffs = new_steps
            if self.anim_initial:
                self.anim_maze = [row[:] for row in self.anim_initial]
            self.anim_frame = 0
            self.anim_active = True
            self.solver = MazeSolver(
                self.maze,
                self.config["OUTPUT_FILE"],
                self.config["ENTRY"],
                self.config["EXIT"],
                self.config["WIDTH"],
                self.config["HEIGHT"],
            )
            path_str = self.solver.solve_maze()
            save_maze_to_file(
                self.maze,
                self.config["OUTPUT_FILE"],
                self.config["WIDTH"],
                self.config["HEIGHT"],
                self.config["ENTRY"],
                self.config["EXIT"],
                path_str
            )
            self._update_solved_path()
        elif keynum == 99:  # 'c' key: Change color theme
            if not self.anim_active:
                self.cm = (self.cm + 1) % len(self.cmodes)
                self._render_maze(self.cm, self.show_path)
        elif keynum == 112:  # 'p' key: Toggle path visibility/animation
            if not self.anim_active and not self.path_anim_active:
                if self.show_path:
                    self.show_path = False
                    self._render_maze(self.cm, self.show_path)
                else:
                    path_str = self.solver.solve_maze()
                    self.path_cells_anim.clear()
                    cy, cx = self.config["ENTRY"]
                    self.path_cells_anim.append((cy, cx))
                    for d in path_str:
                        cy += DIR_MAZE[Directions[d]]
                        cx += DIR_MAZE[Directions[d] + 1]
                        self.path_cells_anim.append((cy, cx))
                    self.path_anim_idx = 0
                    self.path_cells_per_frame = max(
                        1, len(self.path_cells_anim) // self.path_anim_total
                    )
                    self.path_anim_active = True

    def _on_loop(self, param: Any) -> None:
        """Main event loop hook for handling frame-by-frame animations.

        Args:
            param (Any): Unused MLX parameter.

        Returns:
            None
        """
        if self.anim_active and self.anim_maze:
            for _ in range(self.steps_per_frame):
                if self.anim_frame >= len(self.anim_diffs):
                    break
                for dy, dx, val in self.anim_diffs[self.anim_frame]:
                    self.anim_maze[dy][dx] = val
                self.anim_frame += 1

            if self.anim_frame >= len(self.anim_diffs):
                self.anim_active = False
                self._render_maze(self.cm, self.show_path)
                return

            self._draw_maze_structure(self.anim_maze, self.cm, set())
            return

        if self.path_anim_active:
            self.path_anim_idx += self.path_cells_per_frame
            if self.path_anim_idx >= len(self.path_cells_anim):
                self.path_anim_active = False
                self.show_path = True
                self._render_maze(self.cm, self.show_path)
                return
            partial = self.path_cells_anim[: self.path_anim_idx + 1]
            self._render_maze(self.cm, False, partial_path=partial)
            return

    def _on_close(self, param: Any) -> None:
        """Handle window close event.

        Args:
            param (Any): Unused MLX parameter.

        Returns:
            None
        """
        self._cleanup()

    def run(self) -> None:
        """Start the MLX event loop and render the maze."""
        if not self.available:
            return

        self.m.mlx_loop_hook(self.p, self._on_loop, None)
        if not self.anim_active:
            self._render_maze(self.cm, self.show_path)

        self.m.mlx_key_hook(self.win, self._on_key, None)
        self.m.mlx_hook(self.win, 33, 0, self._on_close, None)
        self.m.mlx_loop(self.p)
