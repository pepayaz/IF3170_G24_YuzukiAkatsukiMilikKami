from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Literal
from .dimension import Dimension

@dataclass
class Package:
    id: str
    dimension: Dimension
    value: int
    weight: int
    is_fragile: bool
    eta: int
    position: Position | None
    orientation: Orientation | None
    
    def __init__(self, id: str, dimension: Dimension, value: int,
                 weight: int, is_fragile: bool, eta: int
        ):
        self.id = id
        self.dimension = dimension
        self.value = value
        self.weight = weight
        self.is_fragile = is_fragile
        self.eta = eta
        self.position = None
        self.orientation = None
    
    @staticmethod
    def _rotate_axis(axis: Axis, rotation_axis: Literal["x", "y", "z"],
                     direction: RotationDirection
        ) -> Axis:
        if rotation_axis == "x":
            if direction == RotationDirection.POSITIVE:
                mapping = {
                    "x": "x",
                    "-x": "-x",
                    "y": "z",
                    "-y": "-z",
                    "z": "-y",
                    "-z": "y",
                }
            else:
                mapping = {
                    "x": "x",
                    "-x": "-x",
                    "y": "-z",
                    "-y": "z",
                    "z": "y",
                    "-z": "-y",
                }

        elif rotation_axis == "y":
            if direction == RotationDirection.POSITIVE:
                mapping = {
                    "x": "-z",
                    "-x": "z",
                    "y": "y",
                    "-y": "-y",
                    "z": "x",
                    "-z": "-x",
                }
            else:
                mapping = {
                    "x": "z",
                    "-x": "-z",
                    "y": "y",
                    "-y": "-y",
                    "z": "-x",
                    "-z": "x",
                }

        else:
            if direction == RotationDirection.POSITIVE:
                mapping = {
                    "x": "y",
                    "-x": "-y",
                    "y": "-x",
                    "-y": "x",
                    "z": "z",
                    "-z": "-z",
                }
            else:
                mapping = {
                    "x": "-y",
                    "-x": "y",
                    "y": "x",
                    "-y": "-x",
                    "z": "z",
                    "-z": "-z",
                }

        return mapping[axis]

    def rotate_x(self, direction: RotationDirection):
        self.orientation = Orientation(
            w=self._rotate_axis(self.orientation.w, "x", direction),
            l=self._rotate_axis(self.orientation.l, "x", direction),
            h=self._rotate_axis(self.orientation.h, "x", direction)
        )

    def rotate_y(self, direction: RotationDirection):
        self.orientation = Orientation(
            w=self._rotate_axis(self.orientation.w, "y", direction),
            l=self._rotate_axis(self.orientation.l, "y", direction),
            h=self._rotate_axis(self.orientation.h, "y", direction)
        )

    def rotate_z(self, direction: RotationDirection):
        self.orientation = Orientation(
            w=self._rotate_axis(self.orientation.w, "z", direction),
            l=self._rotate_axis(self.orientation.l, "z", direction),
            h=self._rotate_axis(self.orientation.h, "z", direction)
        )
    
    def move(self, target_position: Position):
        self.position = Position(
            target_position.x,
            target_position.y,
            target_position.z
        )
        
    def is_outside(self):
        return self.position == None
        
Axis = Literal["x", "y", "z", "-x", "-y", "-z"]

@dataclass
class Orientation:
    w: Axis
    l: Axis
    h: Axis
    
@dataclass
class Position:
    x: int
    y: int
    z: int

    def __add__(self, other) -> Position:
        return Position(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z
        )

    def __sub__(self, other) -> Position:
        return Position(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z
        )

    def distance_to(self, other) -> Position:
        return Position(
            other.x - self.x,
            other.y - self.y,
            other.z - self.z
        )

    def translate(self, dx, dy, dz):
        self.x += dx
        self.y += dy
        self.z += dz
        
class RotationDirection(Enum):
    POSITIVE = 1
    NEGATIVE = -1