from dataclasses import dataclass
from enum import Enum
from typing import Literal
from dimension import Dimension

@dataclass
class Package:
    id: str
    dimension: Dimension
    value: int
    weight: int
    is_fragile: bool
    eta: int
    position: Position
    orientation: Orientation
    
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
    
    def rotate_x(self, direction: RotationDirection):
        pass

    def rotate_y(self, direction: RotationDirection):
        pass

    def rotate_z(self, direction: RotationDirection):
        pass
    
    def move(self, position: Position):
        pass
        
@dataclass
class Orientation:
    w: Literal["x", "y", "z", "-x", "-y", "-z"]
    l: Literal["x", "y", "z", "-x", "-y", "-z"]
    h: Literal["x", "y", "z", "-x", "-y", "-z"]
    
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