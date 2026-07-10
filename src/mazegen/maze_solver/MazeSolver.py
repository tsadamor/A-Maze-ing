"""Maze solver module using breadth-first search."""

from collections import deque
from src.mazegen.maze_generator.utils import DIR_MAZE, DIR_NAMES


class MazeSolver:
    """Solver class that finds the shortest path through a maze using BFS.

    Attributes:
        maze (list[list[int]]): 2D list of wall masks.
        file_name (str): Path to output file.
        enter (tuple[int, int]): Start coordinates (row, col).
        exit_coord (tuple[int, int]): End coordinates (row, col).
        width (int): Maze width.
        height (int): Maze height.
    """

    def __init__(
        self,
        maze: list[list[int]],
        file_name: str,
        enter: tuple[int, int],
        exit_coord: tuple[int, int],
        width: int,
        height: int,
    ) -> None:
        """Initialize MazeSolver.

        Args:
            maze (list[list[int]]): 2D list of wall masks.
            file_name (str): Path to output file.
            enter (tuple[int, int]): Start coordinates (row, col).
            exit_coord (tuple[int, int]): End coordinates (row, col).
            width (int): Maze width.
            height (int): Maze height.
        """
        self.maze = maze
        self.file_name = file_name
        self.enter = enter
        self.exit_coord = exit_coord
        self.width = width
        self.height = height
        self._cached_path: str | None = None

    def solve_maze(self) -> str:
        """Find shortest valid path from enter to exit_coord using BFS.

        Returns:
            str: String of directions ('N', 'E', 'S', 'W') for shortest path.
        """
        if self._cached_path is not None:
            return self._cached_path

        result = self._solve_maze_bfs()
        self._cached_path = result if result is not None else ""
        return self._cached_path

    def _solve_maze_bfs(
        self,
        start_node: tuple[int, int] | None = None,
        blocked_cells: set[tuple[int, int]] | None = None,
        blocked_edges: (
            set[tuple[tuple[int, int], tuple[int, int]]] | None
        ) = None,
    ) -> str | None:
        """Helper BFS solver that supports blocked cells and edges."""
        if start_node is None:
            start_node = self.enter
        if blocked_cells is None:
            blocked_cells = set()
        if blocked_edges is None:
            blocked_edges = set()

        def is_valid_coord(h: int, w: int) -> bool:
            return 0 <= h < self.height and 0 <= w < self.width

        if start_node in blocked_cells or self.exit_coord in blocked_cells:
            return None

        queue: deque[tuple[tuple[int, int], str]] = deque([(start_node, "")])
        visited = [[False] * self.width for _ in range(self.height)]
        visited[start_node[0]][start_node[1]] = True

        while queue:
            coord, ans = queue.popleft()
            h, w = coord[0], coord[1]
            if coord == self.exit_coord:
                return ans
            for d in range(4):
                nh, nw = h + DIR_MAZE[d], w + DIR_MAZE[d + 1]
                if not is_valid_coord(nh, nw) or visited[nh][nw]:
                    continue
                if (nh, nw) in blocked_cells:
                    continue
                # Bit positions: N=0, E=1, S=2, W=3
                if self.maze[h][w] & (1 << d):
                    continue
                # Check blocked edge
                if (
                    ((h, w), (nh, nw)) in blocked_edges
                    or ((nh, nw), (h, w)) in blocked_edges
                ):
                    continue
                visited[nh][nw] = True
                queue.append(((nh, nw), ans + DIR_NAMES[d]))

        return None

    def solve_multiple_mazes(self, k: int = 5) -> list[str]:
        """Find up to k shortest unique paths using Yen's algorithm.

        Args:
            k (int): Maximum number of shortest paths to find.

        Returns:
            list[str]: List of unique direction strings.
        """
        p0 = self._solve_maze_bfs()
        if p0 is None:
            return []

        a = [p0]
        b_candidates: set[str] = set()

        for _ in range(1, k):
            prev_path = a[-1]

            # Reconstruct the list of coordinates along the path
            nodes = [self.enter]
            curr = self.enter
            for d_char in prev_path:
                d = DIR_NAMES.index(d_char)
                curr = (curr[0] + DIR_MAZE[d], curr[1] + DIR_MAZE[d + 1])
                nodes.append(curr)

            # Loop over all nodes in the path except the exit
            for i in range(len(nodes) - 1):
                spur_node = nodes[i]
                root_path_str = prev_path[:i]
                root_nodes = nodes[:i + 1]

                blocked_edges = set()
                blocked_cells = set()

                # Block edges of found paths sharing the same root prefix
                for path in a:
                    if len(path) >= i and path[:i] == root_path_str:
                        path_nodes = [self.enter]
                        curr_p = self.enter
                        for d_char in path:
                            d = DIR_NAMES.index(d_char)
                            curr_p = (
                                curr_p[0] + DIR_MAZE[d],
                                curr_p[1] + DIR_MAZE[d + 1],
                            )
                            path_nodes.append(curr_p)

                        if i < len(path_nodes) - 1:
                            u = path_nodes[i]
                            v = path_nodes[i + 1]
                            blocked_edges.add((u, v))

                # Block all nodes in the root path except the spur node
                for node in root_nodes[:-1]:
                    blocked_cells.add(node)

                # Find the spur path from spur node to exit
                spur_path = self._solve_maze_bfs(
                    spur_node, blocked_cells, blocked_edges
                )
                if spur_path is not None:
                    total_path = root_path_str + spur_path
                    if total_path not in a:
                        b_candidates.add(total_path)

            if not b_candidates:
                break

            # Find the path with the minimum length in b_candidates
            sorted_candidates = sorted(
                list(b_candidates), key=lambda x: (len(x), x)
            )
            next_shortest = sorted_candidates[0]
            a.append(next_shortest)
            b_candidates.remove(next_shortest)

        return a
