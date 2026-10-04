from dataclasses import dataclass

@dataclass(frozen=True)
class Dimension:
    w: int
    l: int
    h: int