from __future__ import annotations
from dataclasses import dataclass
from copy import deepcopy

from .truck import Truck
from .package import Package

@dataclass
class Problem:
    trucks: list[Truck]
    packages: list[Package]

@dataclass
class ProblemState:
    problem: Problem
    grid: list[list[list[set[str]]]]

    @property
    def trucks(self) -> list[Truck]:
        return self.problem.trucks

    @property
    def packages(self) -> list[Package]:
        return self.problem.packages

    @property
    def outside_volume(self) -> dict[str, int]:
        outside_volume = {}

        for package in self.packages:
            if package.is_outside():
                continue
            
            dx, dy, dz = package.oriented_offset

            x1 = package.position.x
            x2 = x1 + dx

            y1 = package.position.y
            y2 = y1 + dy

            z1 = package.position.z
            z2 = z1 + dz

            x_min, x_max = min(x1, x2), max(x1, x2)
            y_min, y_max = min(y1, y2), max(y1, y2)
            z_min, z_max = min(z1, z2), max(z1, z2)

            total_volume = (
                package.dimension.w
                * package.dimension.l
                * package.dimension.h
            )

            idx: int = package.truck_idx
            inside_x = max(0, min(x_max, self.trucks[idx].dimension.w - 1) - max(x_min, 0) + 1)
            inside_y = max(0, min(y_max, self.trucks[idx].dimension.l - 1) - max(y_min, 0) + 1)
            inside_z = max(0, min(z_max, self.trucks[idx].dimension.h - 1) - max(z_min, 0) + 1)

            inside_volume = inside_x * inside_y * inside_z

            outside_volume[package.id] = total_volume - inside_volume

        return outside_volume

    @property
    def unloaded_list(self):
        unloaded_list = set()
        for package in self.problem.packages:
            if package.is_outside():
                unloaded_list.add(package.id)
        return unloaded_list

    @property
    def loaded_list(self):
        loaded_list = set()
        for package in self.problem.packages:
            if not package.is_outside():
                loaded_list.add(package.id)
        return loaded_list

    def clone(self):
        return deepcopy(self)

    def rebuild(self):
        from ..utils.state_builder import build_state

        updated = build_state(self.problem)
        self.problem = updated.problem
        self.grid = updated.grid
