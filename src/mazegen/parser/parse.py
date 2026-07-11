"""Configuration parser module using Pydantic for A-Maze-ing project."""

import os
import sys
from typing import Any
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from src.mazegen.utils import get_pattern_42

ERROR_MSG = "Aborted: Bad Configuration File"


class MazeConfig(BaseModel):
    """Pydantic model for validating maze configuration parameters."""

    WIDTH: int = Field(
        ..., gt=1, description="Maze width (must be greater than 1)"
    )
    HEIGHT: int = Field(
        ..., gt=1, description="Maze height (must be greater than 1)"
    )
    ENTRY: tuple[int, int]
    EXIT: tuple[int, int]
    OUTPUT_FILE: str
    PERFECT: bool
    SEED: int | None = None
    ALGORITHM: str | None = None

    @field_validator("WIDTH", mode="before")
    @classmethod
    def parse_width(cls, value: Any) -> int:
        """Validate that width is a positive integer."""
        try:
            parsed_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("WIDTH must be a positive integer.")
        if parsed_val <= 1:
            raise ValueError(
                "WIDTH must be a positive integer greater than 1."
            )
        return parsed_val

    @field_validator("HEIGHT", mode="before")
    @classmethod
    def parse_height(cls, value: Any) -> int:
        """Validate that height is a positive integer."""
        try:
            parsed_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("HEIGHT must be a positive integer.")
        if parsed_val <= 1:
            raise ValueError(
                "HEIGHT must be a positive integer greater than 1."
            )
        return parsed_val

    @field_validator("ENTRY", "EXIT", mode="before")
    @classmethod
    def parse_coordinate(cls, value: Any) -> tuple[int, int]:
        """Convert 'x,y' string into (row, col) i.e. (y, x) integer tuple."""
        if isinstance(value, tuple) and len(value) == 2:
            return value
        if isinstance(value, str):
            parts = value.split(",")
            if len(parts) == 2:
                try:
                    return int(parts[1].strip()), int(parts[0].strip())
                except ValueError:
                    pass
        raise ValueError(
            "Coordinates must be in 'x,y' format "
            "where x and y are integers."
        )

    @field_validator("PERFECT", mode="before")
    @classmethod
    def parse_perfect(cls, value: Any) -> bool:
        """Parse boolean value from string representations."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            val_lower = value.lower()
            if val_lower in ("true", "1", "yes"):
                return True
            elif val_lower in ("false", "0", "no"):
                return False
        raise ValueError(
            "PERFECT must be a boolean value (true/false, 1/0, yes/no)."
        )

    @model_validator(mode="after")
    def validate_maze_constraints(self) -> "MazeConfig":
        """Perform semantic validation on the maze configuration."""
        width = self.WIDTH
        height = self.HEIGHT
        entry_row, entry_col = self.ENTRY
        exit_row, exit_col = self.EXIT

        # Bound checks
        if not (0 <= entry_col < width and 0 <= entry_row < height):
            raise ValueError(
                f"ENTRY coordinate {self.ENTRY} (row, col) is out of bounds "
                f"for maze of size {width}x{height}."
            )
        if not (0 <= exit_col < width and 0 <= exit_row < height):
            raise ValueError(
                f"EXIT coordinate {self.EXIT} (row, col) is out of bounds "
                f"for maze of size {width}x{height}."
            )

        # Duplicate check
        if self.ENTRY == self.EXIT:
            raise ValueError("ENTRY and EXIT coordinates cannot be the same.")

        # Pattern 42 collision check
        pattern_42 = get_pattern_42(width, height)
        if self.ENTRY in pattern_42:
            raise ValueError(
                "ENTRY coordinate cannot be inside the '42' pattern."
            )
        if self.EXIT in pattern_42:
            raise ValueError(
                "EXIT coordinate cannot be inside the '42' pattern."
            )

        return self


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
                conf_result[key.strip()] = value.strip()
    except OSError:
        return (False, {})

    return (True, conf_result)


def parser(file_name: str) -> tuple[bool, dict[str, Any]]:
    """Main entrypoint for parsing and validating maze configuration file.

    Args:
        file_name (str): Path to configuration file.

    Returns:
        tuple[bool, dict[str, Any]]: A tuple containing:
            - bool: Success indicator.
            - dict[str, Any]: Validated configuration dictionary.
    """
    success, raw_config = parse_file(file_name)
    if not success:
        print(ERROR_MSG)
        return (False, {})

    try:
        config = MazeConfig.model_validate(raw_config)
        return (True, config.model_dump())
    except ValidationError as error:
        print(ERROR_MSG)
        # Detailed errors to stderr
        for err_details in error.errors():
            location = ".".join(str(x) for x in err_details["loc"])
            message = err_details["msg"]
            print(
                f"  - Validation Error on '{location}': {message}",
                file=sys.stderr
            )
        return (False, {})
