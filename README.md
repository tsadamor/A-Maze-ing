*This project has been created as part of the 42 curriculum by tsadamor, hfujisad.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator and visualizer. It reads a configuration
file, generates a maze, writes the result as hexadecimal wall data, stores a
solution path, and displays the maze in an interactive window.

The project supports two generation modes:

- `PERFECT=True`: generate a perfect maze with exactly one route between cells.
- `PERFECT=False`: generate a Pac-Man-like board with loops and alternate
  routes. Dead-ends are removed except for the central `42` pattern area.

The generated maze contains a visible `42` pattern made from closed cells when
the maze is large enough to fit it.

## Instructions

### Requirements

- Python 3.10 or later
- The project dependencies used by the visualizer, including `mlx` and
  `pyautogui`

### Run

```sh
python3 a_maze_ing.py config.txt
```

The current program reads the default `config.txt` file from the repository
root.

### Controls

- `R`: regenerate the maze
- `P`: show or hide a path
- `C`: change wall colors
- `Esc`: quit

For `PERFECT=False`, the displayed path can change because the board contains
multiple valid routes.

## Configuration File

The configuration file uses one `KEY=VALUE` pair per line. Lines beginning with
`#` are ignored.

Required keys:

```txt
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
OUTPUT_FILE=maze.txt
PERFECT=False
```

Optional keys:

```txt
SEED=42
```

Key details:

- `WIDTH`: maze width in cells
- `HEIGHT`: maze height in cells
- `ENTRY`: entry coordinate as `x,y`
- `EXIT`: exit coordinate as `x,y`
- `OUTPUT_FILE`: file where the encoded maze is written
- `PERFECT`: `True` for a perfect maze, `False` for a looped board
- `SEED`: optional integer used for reproducible generation

## Output Format

Each maze cell is written as one hexadecimal digit. The digit encodes closed
walls with four bits:

| Bit | Direction |
| --- | --- |
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

After the maze grid, the output file contains an empty line, then:

1. the entry coordinate
2. the exit coordinate
3. a valid solution path using `N`, `E`, `S`, and `W`

## Generation Algorithm

The base maze is generated with recursive backtracking, implemented iteratively
with a stack.

Why this algorithm was chosen:

- It naturally creates a perfect maze when no extra passages are added.
- It is simple to reason about and easy to verify.
- It works well with a seed, so generation can be reproduced.
- It produces a connected maze without isolated corridor cells.

For `PERFECT=False`, the generated perfect maze is passed through a braid step.
This step opens additional internal walls to remove normal dead-ends and create
loops. It preserves the entry, exit, four corners, center cell, and the visible
`42` pattern. Dead-ends caused directly by the central `42` pattern are allowed.

## Reusable Module

The reusable generation logic is centered on:

```txt
maze_generator/MazeGenerator.py
```

Basic example:

```python
from maze_generator.MazeGenerator import MazeGenerator

config = {
    "WIDTH": 20,
    "HEIGHT": 20,
    "ENTRY": (0, 0),
    "EXIT": (19, 19),
    "OUTPUT_FILE": "maze.txt",
    "PERFECT": False,
    "SEED": 42,
}

generator = MazeGenerator(config)
maze = generator.generate_maze()
generator.save_maze_to_file()
```

Accessing generated data:

- `maze` is a `list[list[int]]`
- Each integer uses the hexadecimal wall encoding described above
- `generate_maze_steps()` returns the final maze plus animation diffs

The package metadata is defined in `pyproject.toml` under the package name
`mazegen`. A wheel file can be built from the project sources and installed in a
future project.

The reusable generator is distributed under the MIT License. See `LICENSE.md`
for the full license text.

## Project Structure

```txt
a_maze_ing.py                 Main program and visualizer
config.txt                    Default configuration file
parser/parse.py               Configuration parser and validator
maze_generator/               Reusable maze generation package
maze_generator/backtracking.py Perfect maze generation
maze_generator/braid.py        Non-perfect loop and dead-end handling
maze_generator/utils/          42 pattern helpers
maze_solver/MazeSolver.py      Path solving and output path writing
pyproject.toml                Build metadata for mazegen
```

## Team and Project Management

Team members:

- tsadamor: implemented the recursive backtracking generator, created and moved
  the `42` pattern helpers, added the reusable `MazeGenerator` class, added seed
  support, fixed parser behavior, created the program entry point, and handled
  packaging/build setup such as `pyproject.toml` and wheel placement.
- hfujisad: implemented the initial parser validation, added the wall expansion
  generator prototype, built the maze solver and output path integration,
  developed the visualizer, added regeneration/recolor/path controls, improved
  visualization performance, added generation animation, fixed coordinate
  handling, and implemented the non-perfect/bonus board behavior.

This split was checked against the Git history with `git log`, including commit
messages for the generator, parser, solver, visualizer, seed, packaging,
animation, and bonus/non-perfect work.

Planning:

- First, define the configuration and output format.
- Then, implement a perfect maze generator.
- Add visualization and keyboard controls.
- Extend the generator for non-perfect Pac-Man-like boards.
- Finish by checking edge cases, README content, and reusable package metadata.

What worked well:

- Keeping generation, parsing, solving, and visualization in separate modules
  made it easier to change one part without rewriting the rest.
- Using a seed made behavior reproducible while debugging.

What could be improved:

- Add automated tests for parser errors, wall coherence, dead-end counts, and
  path validity.
- Add more automated checks to the Makefile as the project grows.
- Exclude virtual environments from full lint runs so external dependencies are
  not checked by `flake8`.

Tools used:

- Python 3.10
- flake8 and mypy for code checks
- AI assistance for implementation review, README drafting, and checking edge
  cases around `PERFECT=False`

## Resources

- Python documentation: https://docs.python.org/3/
- Python packaging guide: https://packaging.python.org/
- Recursive backtracking maze generation:
  https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Graph theory background for spanning trees:
  https://en.wikipedia.org/wiki/Spanning_tree

AI was used as a development assistant for:

- summarizing project requirements
- comparing generation strategies
- drafting and revising small implementation changes
- checking generated maze properties such as loops and dead-ends
- writing this README

All generated suggestions were reviewed and adapted to match the project code.
