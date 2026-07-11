"""Directions definition for A-Maze-ing project."""

from enum import IntEnum


class DirectionMask(IntEnum):
    """Cardinal directions bitmask values."""

    NORTH = 1 << 0
    EAST = 1 << 1
    SOUTH = 1 << 2
    WEST = 1 << 3
