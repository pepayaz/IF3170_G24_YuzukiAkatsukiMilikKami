from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy

from .truck import Truck
from .package import Package

@dataclass
class Problem:
    truck: Truck
    packages: list[Package]
    grid: list[list[list[set[str]]]]  # grid[z][y][x]
    outside_volume: dict[str, int]

    @property
    def loaded_list(self):
        unloaded_list = set()
        for package in self.problem.packages:
            if package.position is None:
                unloaded_list.add(package.id)
        return unloaded_list
    
    @property
    def loaded_list(self):
        loaded_list = set()
        for package in self.problem.packages:
            if package.position is not None:
                loaded_list.add(package.id)
        return loaded_list

    def clone(self):
        return deepcopy(self)