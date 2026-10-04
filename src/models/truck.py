from dataclasses import dataclass
from dimension import Dimension

@dataclass(frozen=True)
class Truck:
    dimension: Dimension
    max_capacity: int