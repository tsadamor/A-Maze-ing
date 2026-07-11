"""Configuration parser module using Pydantic for A-Maze-ing project."""

import os
import sys
from typing import Any

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ValidationInfo,
    field_validator,
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

    @field_validator("ENTRY", "EXIT")
    @classmethod
    def validate_coordinate_constraints(
        cls, coordinate: tuple[int, int], info: ValidationInfo
    ) -> tuple[int, int]:
        """Validate coordinate bounds, uniqueness, and pattern collision."""
        width = info.data.get("WIDTH")
        height = info.data.get("HEIGHT")
        if width is None or height is None:
            return coordinate
        row, col = coordinate
        field_name = info.field_name

        if not (0 <= col < width and 0 <= row < height):
            raise ValueError(
                f"{field_name} coordinate {coordinate} (row, col) is out of "
                "bounds "
                f"for maze of size {width}x{height}."
            )
        if field_name == "EXIT" and coordinate == info.data.get("ENTRY"):
            raise ValueError("ENTRY and EXIT coordinates cannot be the same.")
        pattern_42 = get_pattern_42(width, height)
        if coordinate in pattern_42:
            raise ValueError(
                f"{field_name} coordinate cannot be inside the '42' pattern."
            )
        return coordinate


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
                conf_result[key.strip().upper()] = value.strip()
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
        missing_fields = []
        other_errors = []
        for err_details in error.errors():
            location = ".".join(str(x) for x in err_details["loc"])
            if err_details["type"] == "missing":
                missing_fields.append(location)
            else:
                other_errors.append((location, err_details["msg"]))

        if missing_fields:
            joined = ', '.join(missing_fields)
            print(f"Aborted: Missing configuration fields: {joined}")
        elif other_errors:
            print(ERROR_MSG, file=sys.stderr)

        for loc, msg in other_errors:
            print(f"Validation Error on '{loc}': {msg}", file=sys.stderr)
        return (False, {})
