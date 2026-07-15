*This project has been created as part of the 42 curriculum by tsadamor and hfujisad.*

# A-Maze-ing

## Description
**A-Maze-ing** is a Python-based reusable maze generation and solving library and application built as part of the 42 curriculum. The project implements multiple algorithms for generating random mazes, including randomized Depth-First Search (DFS) for perfect academic mazes, a custom Pac-Man style braided maze algorithm, and a Wall Expansion (Wilson's-like) algorithm. It includes an interactive visual rendering interface using the MiniLibX (MLX) library.

The generator supports saving the generated maze configuration to a file in a custom hexadecimal format, along with its shortest-path solution coordinates and directional instructions.

---

## Configuration File Format
The program is driven by a `key=value` configuration file (default is `config.txt`). Lines starting with `#` are ignored as comments.

### Mandatory Keys:
- **`WIDTH`**: The number of cells horizontally (must be $> 1$).
- **`HEIGHT`**: The number of cells vertically (must be $> 1$).
- **`ENTRY`**: The coordinates of the entrance cell, formatted as `x,y` (0-indexed).
- **`EXIT`**: The coordinates of the exit cell, formatted as `x,y` (0-indexed).
- **`OUTPUT_FILE`**: The filename where the generated maze and its solution path will be written.
- **`PERFECT`**: A boolean (`True`/`False` or `1`/`0`) determining if the maze is a perfect maze (exactly one unique path from entrance to exit) or a braided/playable Pac-Man-style maze.

### Optional Keys:
- **`SEED`**: Integer seed value for reproducing random generations.

#### Example `config.txt`:
```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

---

## Instructions

### Prerequisites
- Python 3.10 or later.
- `uv` package manager (optional, but recommended by Makefile) or `pip`.

### Setup & Run Commands via Makefile:
The project provides a `Makefile` to automate all key development tasks:

1. **Installation**:
   Installs the `mazegen` wheel package along with its dev dependencies:
   ```bash
   make install
   ```
2. **Run Application**:
   Executes the main entry point with the default config:
   ```bash
   make run
   ```
3. **Debug Mode**:
   Launches the main script using Python's built-in debugger (`pdb`):
   ```bash
   make debug
   ```
4. **Code Quality Linting**:
   Runs standard `flake8` checks and strict `mypy` type analysis:
   ```bash
   make lint
   ```
   Or for strict typing checks:
   ```bash
   make lint-strict
   ```
5. **Clean Build Caches**:
   Cleans up local virtual environment, caches, build wheels, and python binaries:
   ```bash
   make clean
   ```

---

## Maze Generation Algorithms

The project supports three distinct maze generation algorithms to fulfill the requirements of different play styles:

### 1. Randomized Depth-First Search (`dfs`)
- **Type**: Perfect Maze generator.
- **Behavior**: Uses a stack-based backtracking approach to carve out passages. It ensures that every cell in the grid is visited and that there is exactly one unique path between any two points (no loops, no isolated cells).
- **Why chosen**: It is the classic academic algorithm for generating perfect mazes, characterized by long, winding corridors.

### 2. Pac-Man Style Braided Maze (`pacman`)
- **Type**: Braided Maze (playable board).
- **Behavior**: Starts from a perfect DFS maze and iteratively removes dead-ends by opening adjacent walls. It guarantees full connectivity (every corridor is reachable) while ensuring multiple independent routes (loops) exist so that a player can never be trapped.
- **Why chosen**: Specially designed for Pac-Man-like gameplay, ensuring no dead-ends and providing a balanced distribution of open corridors.

### 3. Wall Expansion (`wall_expand`)
- **Type**: Perfect/Dual-Spanning Tree Maze generator.
- **Behavior**: Grows wall segments from the outer boundaries inward using a random loop-erased wall expansion algorithm. It prevents loops and isolates blocks of the maze, forming a perfect maze structure.
- **Why chosen**: It was a contrasting algorithm because, unlike DFS—which generates a grid surrounded by walls and then creates a maze by destroying those walls—.

---

## Reusable Package Structure
The maze generator is designed as a standalone, modular package called `mazegen`. It can be easily built into a Python wheel (`.whl`) or source distribution (`.tar.gz`) for packaging.

### Code Reusability and API:
The core generation and solving logic is fully decoupled from the GUI visualization:
- **`MazeGenerator`** `MazeGenerator.py` : Exposes initialization, generation, and output/export capabilities.
- **`MazeSolver`** `MazeSolver.py` : Solves any 2D grid representation using Breadth-First Search (BFS) and outputs coordinates and directional solutions.
- **`parser`** `parse.py`: Formats and validates input files.

#### API Example:
```python
from mazegen import MazeGenerator

# Initialize generator
generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_coord=(14, 19),
    perfect=True,
    seed=42
)

# Generate maze grid structure
maze_grid = generator.generate_maze()

# Get solved path coordinates
path_coords = generator.get_solution_path()
print("Solution Path:", path_coords)
```

---

## Resources
- **DFS / Backtracking**: [Maze Generation Algorithms on Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm), [The Bucksblog](https://www.jamisbuck.org/mazes/)
- **MiniLibX (MLX)**: [42_MiniLibX_Python_Manual](https://github.com/SaraFreitas-dev/MLX-42lib-Helpfull-Documentation/blob/main/MLX_DOCUMENTATION.md)
- **Pydantic**: [Pydantic Docs](https://pydantic.dev/docs/validation/latest/get-started/)
- **uv**: [uv docs](https://docs.astral.sh/uv/)

### AI Usage Description:
AI(Gemini, Codex) was used to:
- Documentation Support
- Conceputual Learning
- Refactoring parser, the algorithm for Pac-Man playable maze, and Visualization
---

## Team & Project Management

### Roles:
- **tsadamor**:
  - Developed the core Depth-First Search (DFS) / Backtracking maze generation algorithm and configured the central "42" pattern layout.
  - Set up Python packaging config (`pyproject.toml`), `.whl` package distribution, and dependency management.
  - Created the project CLI entrypoint (`a_maze_ing.py`), config file parsing verification, and the automation `Makefile`.
- **hfujisad**:
  - Developed the graphical MLX visualizer interface, adding real-time generation animations, solution path visual effects, color theme rotation (`C`), and on-the-fly maze regeneration (`R`).
  - Implemented the Wall Expansion (`wall_expand`) maze generation algorithm.
  - Designed the `MazeSolver` class using Breadth-First Search (BFS) to solve mazes and compute the shortest path.
  - Standardized the coordinate mapping across components (unifying width/height variables) and resolved parser boundary checks.

### Planning & Evolution:
1. **Phase 1**: Base algorithm implementations (DFS/Backtracking and Wall Expansion) & configuration file parsing.
2. **Phase 2**: Designing the MLX graphical visualizer and integrating solver/generator animation flows.
3. **Phase 3**: Strict code style compliance and type correctness adjustments using `flake8` and `mypy`.
4. **Phase 4**: Project packaging, build automation via `Makefile`, and performance optimization of rendering routines.
5. **Phase 5**: Implementation of the new requirements, such as Pac-Man playable, License.md, etc...

### Lessons Learned:
- **What worked well**: Separating the parser, solver, generator, and visualizer modules allowed for seamless parallel development and clean integration.
- **Changes from the original plan**: Since the 42 side changed the subject without notice after the initial registration, the new requirements came as a complete surprise.
- **Improvements**: Optimizing visualizer frame-update throughput greatly improved responsiveness. Future iterations could benefit from adding more solving algorithms (such as A* or Dijkstra's).

### Tools Used:
- **`uv`**: Fast Python package installer and workspace manager.
- **`mypy` & `flake8`**: Strict type checking and code style validation.
- **`mlx`**: Python bindings of MiniLibX for the interactive graphic window.
