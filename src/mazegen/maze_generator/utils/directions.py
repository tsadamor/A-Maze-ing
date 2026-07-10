"""Directions definition for A-Maze-ing project."""

from enum import IntEnum


class Directions(IntEnum):
    """Cardinal directions bit positions."""

    N = 0
    E = 1
    S = 2
    W = 3


class DirectionMask(IntEnum):
    """Cardinal directions bitmask values."""

    NORTH = 1 << Directions.N
    EAST = 1 << Directions.E
    SOUTH = 1 << Directions.S
    WEST = 1 << Directions.W


DIR_MAZE = [-1, 0, 1, 0, -1]
DIR_NAMES = ["N", "E", "S", "W"]
