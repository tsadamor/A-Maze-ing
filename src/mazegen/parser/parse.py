"""Configuration parser module for A-Maze-ing project."""

import os
from typing import Any

from src.mazegen.maze_generator.utils import get_pattern_42

MANDATORY_KEYS = [
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
]

ERROR_MSG = "Aborted: Bad Configuration File"


def parse_file(file_name: str) -> tuple[bool, dict[str, str]]:
    """Parse key=value configuration file into a dictionary of strings.

    Args:
        file_name (str): Path to configuration text file.

    Returns:
        tuple[bool, dict[str, str]]: A tuple containing:
            - bool: Success indicator.
            - dict[str, str]: Raw string configuration dictionary.
    """
    if not os.path.isfile(file_name):
        return (False, {})

    conf_result: dict[str, str] = {}
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                equal_count = line.count("=")
                if equal_count != 1:
                    return (False, {})
                key, value = line.split("=")
                key = key.strip()
                value = value.strip()
                conf_result[key] = value
    except OSError:
        return (False, {})

    for key in MANDATORY_KEYS:
        if key not in conf_result:
            return (False, {})
    return (True, conf_result)


def convert_config_data(
    conf: dict[str, str],
) -> tuple[bool, dict[str, Any]]:
    """Convert raw config values into appropriate Python data types.

    Args:
        conf (dict[str, str]): Raw string dictionary of
            configuration parameters.

    Returns:
        tuple[bool, dict[str, Any]]: A tuple containing:
            - bool: Success indicator.
            - dict[str, Any]: Converted configuration dictionary.
    """
    converted_res: dict[str, Any] = {}
    for key, value in conf.items():
        if key in ("WIDTH", "HEIGHT"):
            try:
                converted_res[key] = int(value)
            except ValueError:
                return (False, {})
        elif key in ("ENTRY", "EXIT"):
            try:
                coords = value.split(",")
                if len(coords) != 2:
                    return (False, {})
                x, y = int(coords[0].strip()), int(coords[1].strip())
                # Store coordinates as (row, col) i.e. (y, x)
                converted_res[key] = (y, x)
            except ValueError:
                return (False, {})
        elif key == "PERFECT":
            val_lower = value.lower()
            if val_lower in ("true", "1", "yes"):
                converted_res[key] = True
            elif val_lower in ("false", "0", "no"):
                converted_res[key] = False
            else:
                return (False, {})
        elif key == "SEED":
            try:
                converted_res[key] = int(value)
            except ValueError:
                return (False, {})
        else:
            converted_res[key] = value

    if "SEED" not in converted_res:
        converted_res["SEED"] = None

    return (True, converted_res)


def is_valid_dict(conf: dict[str, Any]) -> bool:
    """Validate semantic constraints on configuration dictionary.

    Args:
        conf (dict[str, Any]): Converted configuration dictionary.

    Returns:
        bool: True if valid, False otherwise.
    """
    maze_width: int = conf["WIDTH"]
    maze_height: int = conf["HEIGHT"]
    entry_row, entry_col = conf["ENTRY"]
    exit_row, exit_col = conf["EXIT"]

    if maze_width <= 1 or maze_height <= 1:
        return False
    if not (0 <= entry_col < maze_width and 0 <= entry_row < maze_height):
        return False
    if not (0 <= exit_col < maze_width and 0 <= exit_row < maze_height):
        return False
    if conf["ENTRY"] == conf["EXIT"]:
        return False

    pattern_42 = get_pattern_42(maze_width, maze_height)
    if conf["ENTRY"] in pattern_42 or conf["EXIT"] in pattern_42:
        return False

    return True


def parser(file_name: str) -> tuple[bool, dict[str, Any]]:
    """Main entrypoint for parsing and validating maze configuration file.

    Args:
        file_name (str): Path to configuration file.

    Returns:
        tuple[bool, dict[str, Any]]: A tuple containing:
            - bool: Success indicator.
            - dict[str, Any]: Validated configuration dictionary.
    """
    initial_parse_result = parse_file(file_name)
    if not initial_parse_result[0]:
        print(ERROR_MSG)
        return (False, {})

    converted_parse_result = convert_config_data(initial_parse_result[1])
    if not converted_parse_result[0]:
        print(ERROR_MSG)
        return (False, {})

    if not is_valid_dict(converted_parse_result[1]):
        print(ERROR_MSG)
        return (False, {})

    return (True, converted_parse_result[1])
