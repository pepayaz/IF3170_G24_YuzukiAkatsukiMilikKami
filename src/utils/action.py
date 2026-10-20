from __future__ import annotations

from ..models.problem import ProblemState
from ..models.package import Package, Orientation, Position, Axis, RotationDirection

import random

def get_random_location(state: ProblemState) -> tuple[Position, int]:
    truck_idx = random.randrange(len(state.trucks))
    dimension = state.trucks[truck_idx].dimension
    x = random.randrange(dimension.w)
    y = random.randrange(dimension.l)
    z = random.randrange(dimension.h)
    return Position(x, y, z), truck_idx

def generate_random_successor(state: ProblemState) -> ProblemState:
    action = random.choice(["move_package", "swap_package", "rotate_package"])

    if action == "move_package":
        package = random.choice(state.packages)
        position, truck_idx = get_random_location(state)
        return move_package(state, package.id, position, truck_idx)

    elif action == "swap_package":
        package_1, package_2 = random.sample(state.packages, 2)
        return swap_package(state, package_1.id, package_2.id)

    else:
        inside_packages = []
        for package in state.packages:
            if not package.is_outside():
                inside_packages.append(package)
        
        # Kalau package diluar semua, successor selanjutnya masukin random
        if len(inside_packages) == 0:
            package = random.choice(state.packages)
            position, truck_idx = get_random_location(state)
            return move_package(state, package.id, position, truck_idx)

        package = random.choice(inside_packages)
        axis = random.choice(["x", "-x", "y", "-y", "z", "-z"])

        return rotate_package(state, package.id, axis)

def generate_all_successor(state: ProblemState) -> list[ProblemState]:
    all_successor = []

    # Pindah setiap paket ke setiap koordinat truk
    for package in state.packages:
        for truck_idx in range(len(state.trucks)):
            dimension = state.trucks[truck_idx].dimension
            for z in range(dimension.h):
                for y in range(dimension.l):
                    for x in range(dimension.w):

                        if package.position is not None and package.truck_idx == truck_idx:
                            # Posisi yang sama ga di pindah
                            if (package.position.x == x and package.position.y == y and package.position.z == z):
                                continue

                        position = Position(x, y, z)
                        successor = move_package(state, package.id, position, truck_idx)
                        all_successor.append(successor)

    # Tukar setiap pasangan package
    for i in range(len(state.packages)):
        for j in range(i + 1, len(state.packages)):
            package_1 = state.packages[i]
            package_2 = state.packages[j]

            successor = swap_package(state, package_1.id, package_2.id)
            all_successor.append(successor)

    # Rotate paket di truk
    for package in state.packages:
        if package.is_outside():
            continue # Ga rotate kalau diluar

        for axis in ["x", "-x", "y", "-y", "z", "-z"]:
            successor = rotate_package(state, package.id, axis)
            all_successor.append(successor)

    return all_successor

def rotate_package(state: ProblemState, id: str, rotation_axis: Axis) -> ProblemState:
    updated = state.clone()
    package = get_package(updated, id)
    initial_orientation = package.orientation

    sign = RotationDirection.NEGATIVE if rotation_axis.startswith('-') else RotationDirection.POSITIVE
    axis = rotation_axis.lstrip('-')

    if axis == 'x':
        package.rotate_x(sign)
    elif axis == 'y':
        package.rotate_y(sign)
    elif axis == 'z':
        package.rotate_z(sign)
    else:
        raise RuntimeError(f"Invalid axis: {axis}")

    _update_grid(state, updated, id)

    return updated

def _update_grid(origin: ProblemState, updated: ProblemState, id: str):
    old_package = get_package(origin, id)
    package = get_package(updated, id)

    if old_package.position is not None:
        _apply_cells(updated, old_package.truck_idx, get_occupied_cells(old_package), package.id, add=False)

    if package.position is not None:
        _apply_cells(updated, package.truck_idx, get_occupied_cells(package), package.id, add=True)

def _apply_cells(state: ProblemState, truck_idx: int, cells, package_id: str, add: bool):
    truck_grid = state.grid[truck_idx]
    depth = len(truck_grid)
    height = len(truck_grid[0])
    width = len(truck_grid[0][0])

    for x, y, z in cells:
        if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
            if add:
                truck_grid[z][y][x].add(package_id)
            else:
                truck_grid[z][y][x].discard(package_id)


def move_package(state: ProblemState, id: str, target: Position, truck_idx: int | None = None) -> ProblemState:
    updated = state.clone()
    package = get_package(updated, id)

    if truck_idx is None:
        truck_idx = package.truck_idx if package.truck_idx is not None else 0

    package.move(target, truck_idx)

    _update_grid(state, updated, id)

    return updated


def swap_package(state: ProblemState, id1: str, id2: str) -> ProblemState:
    updated = state.clone()
    package1 = get_package(updated, id1)
    package2 = get_package(updated, id2)

    pos1, truck1 = package1.position, package1.truck_idx
    pos2, truck2 = package2.position, package2.truck_idx

    package1.move(pos2, truck2)
    package2.move(pos1, truck1)

    _update_grid(state, updated, id1)
    _update_grid(state, updated, id2)

    return updated


def get_package(state: ProblemState, id: str) -> Package | None:
    for package in state.packages:
        if package.id == id:
            return package

    return None

def get_occupied_cells(package: Package) -> set[(int, int, int)]:
    cells = set()
    
    if package.position is None:
        return cells
    
    dim = {
        'x': 0,
        'y': 0,
        'z': 0,
    }

    dim['x'], dim['y'], dim['z'] = package.oriented_offset
    position = package.position

    starts = {
        'x': position.x,
        'y': position.y,
        'z': position.z,
    }

    for axis in ('x', 'y', 'z'):
        start = starts[axis]
        end = start + dim[axis]

        axis_range = range(min(start, end), max(start, end) + 1)

        if axis == 'x':
            x_range = axis_range
        elif axis == 'y':
            y_range = axis_range
        else:
            z_range = axis_range

    for z in z_range:
        for y in y_range:
            for x in x_range:
                cells.add((x, y, z))

    return cells