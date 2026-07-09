import os
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError
from pydantic import field_validator, model_validator

Coord = tuple[int, int]

ERROR_MSG = "Aborted: Bad Configuration File"


class MazeConfig(BaseModel):
    """Typed and validated representation of a maze configuration file."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    width: int = Field(alias="WIDTH")
    height: int = Field(alias="HEIGHT")
    entry: Coord = Field(alias="ENTRY")
    exit_coord: Coord = Field(alias="EXIT")
    output_file: str = Field(alias="OUTPUT_FILE")
    perfect: bool = Field(alias="PERFECT")
    seed: int | None = Field(default=None, alias="SEED")

    @field_validator("entry", "exit_coord", mode="before")
    @classmethod
    def parse_coord(cls, value: object) -> Coord:
        """Convert 'x,y' into internal (row, column)."""
        if isinstance(value, str):
            parts = value.split(",")
            if len(parts) != 2:
                raise ValueError("coordinate must be x,y")
            x_str, y_str = parts
            return (int(y_str), int(x_str))
        if (
            isinstance(value, tuple)
            and len(value) == 2
            and all(isinstance(item, int) for item in value)
        ):
            return value
        raise ValueError("coordinate must be x,y")

    @model_validator(mode="after")
    def validate_bounds(self) -> "MazeConfig":
        """Validate dimensions and coordinate bounds."""
        if self.width <= 1 or self.height <= 1:
            raise ValueError("width and height must be greater than 1")
        if self.entry == self.exit_coord:
            raise ValueError("entry and exit must be different")
        self._validate_coord(self.entry)
        self._validate_coord(self.exit_coord)
        return self

    def _validate_coord(self, coord: Coord) -> None:
        row, column = coord
        if column < 0 or row < 0:
            raise ValueError("coordinates must be non-negative")
        if self.width <= column or self.height <= row:
            raise ValueError("coordinates must be inside maze bounds")

    def to_runtime_dict(self) -> dict[str, Any]:
        """Return the uppercase-key runtime dictionary."""
        return self.model_dump(by_alias=True)


def parse_file(file_name: str) -> tuple[bool, dict[str, str]]:
    """Parse KEY=VALUE lines from the configuration file."""
    if not os.path.isfile(file_name):
        return (False, {})

    conf_result: dict[str, str] = {}
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.count("=") != 1:
                return (False, {})
            key, value = line.split("=")
            conf_result[key] = value
    return (True, conf_result)


def parser(file_name: str) -> tuple[bool, dict[str, Any]]:
    """Load and validate a maze configuration file."""
    parse_result = parse_file(file_name)
    if not parse_result[0]:
        print(ERROR_MSG)
        return (False, {})

    try:
        config = MazeConfig.model_validate(parse_result[1])
    except (ValidationError, ValueError):
        print(ERROR_MSG)
        return (False, {})

    return (True, config.to_runtime_dict())
