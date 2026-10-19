from __future__ import annotations

from ..models.problem import ProblemState
from ..models.package import Package, Orientation, Position, Axis, RotationDirection

def generate_random_successor(state: ProblemState) -> ProblemState:
    pass #todo


def generate_all_successor(state: ProblemState) -> ProblemState:
    pass #todo


def rotate_package(state: ProblemState, id: str, rotation_axis: Axis) -> ProblemState:
    updated = state.clone()
    package = get_package(updated, id)
    initial_orientation = package.orientation

    sign = -1 if rotation_axis.startswith('-') else 1
    axis = rotation_axis.lstrip('-')

    if axis == 'x':
        package.rotate_x(sign)
    elif axis == 'y':
        package.rotate_y(sign)
    elif axis == 'z':
        package.rotate_z(sign)
    else:
        raise RuntimeError(f"Invalid axis: {axis}")

    _update_grid_rotate(updated, id, initial_orientation)

    return updated

def _update_grid_rotate(origin: ProblemState, updated: ProblemState, id: str):
    package = get_package(updated,id)
    old_cells = get_occupied_cells(get_package(origin, id))
    new_cells = get_occupied_cells(package)

    depth = len(updated.grid)
    height = len(updated.grid[0])
    width = len(updated.grid[0][0])

    # Hapus data package dari grid lama
    for x, y, z in old_cells:
        if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
            updated.grid[z][y][x].discard(package.id)

    # Masukkan data package ke grid baru
    for x, y, z in new_cells:
        if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
            updated.grid[z][y][x].add(package.id)


def move_package(state: ProblemState, id: str, target: Position) -> ProblemState:
    updated = state.clone()
    package = get_package(updated, id)

    package.move(target)

    _update_grid_move(state, updated, id)

    return updated

def _update_grid_move(origin: ProblemState, updated: ProblemState, id: str):
    package = get_package(updated, id)
    old_cells = get_occupied_cells(get_package(origin, id))
    new_cells = get_occupied_cells(package)

    depth = len(updated.grid)
    height = len(updated.grid[0])
    width = len(updated.grid[0][0])

    # Hapus data package dari grid lama
    for x, y, z in old_cells:
        if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
            updated.grid[z][y][x].discard(package.id)

    # Masukkan data package ke grid baru
    for x, y, z in new_cells:
        if 0 <= x < width and 0 <= y < height and 0 <= z < depth:
            updated.grid[z][y][x].add(package.id)


def swap_package(state: ProblemState, id1: str, id2: str) -> ProblemState:
    updated = state.clone()
    package1 = get_package(updated, id1)
    package2 = get_package(updated, id2)

    pos1 = package1.position
    pos2 = package2.position

    package1.move(pos2)
    package2.move(pos1)

    _update_grid_move(state, updated, id1)
    _update_grid_move(state, updated, id2)

    return updated


def get_package(state: ProblemState, id: str) -> Package | None:
    for package in state.packages:
        if package.id == id:
            return package

    return None

def get_occupied_cells(package: Package) -> set[Position]:
    sizes = {
        'w': package.dimension.w,
        'l': package.dimension.l,
        'h': package.dimension.h,
    }

    dim = package.oriented_dimension
    position = package.position

    starts = {
        'x': position.x,
        'y': position.y,
        'z': position.z,
    }

    cells = set()

    for axis in ('x', 'y', 'z'):
        start = starts[axis]
        end = start + dim[axis]

        axis_range = range(min(start, end), max(start, end))

        if axis == 'x':
            x_range = axis_range
        elif axis == 'y':
            y_range = axis_range
        else:
            z_range = axis_range

    for z in z_range:
        for y in y_range:
            for x in x_range:
                cells.add(Position(x, y, z))

    return cells