from ..models.package import Position
from ..models.problem import Problem, ProblemState
from .input_loader import (
    InputError,
    read_integer,
    read_orientation,
    read_packages,
    read_truck,
)


def copy_problem(problem):
    truck = problem.truck
    dimension = truck.dimension
    truck_data = {
        "dimension": {"w": dimension.w, "l": dimension.l, "h": dimension.h},
        "max_capacity": truck.max_capacity
    }
    new_truck = read_truck(truck_data)

    package_data = []
    for package in problem.packages:
        dimension = package.dimension
        package_data.append({
            "id": package.id,
            "dimension": {"w": dimension.w, "l": dimension.l, "h": dimension.h},
            "value": package.value,
            "weight": package.weight,
            "is_fragile": package.is_fragile,
            "eta": package.eta
        })
    new_packages = read_packages(package_data)

    for index in range(len(problem.packages)):
        original = problem.packages[index]
        copied = new_packages[index]
        location = "package." + original.id
        orientation = original.orientation

        if orientation is None:
            raise InputError(location + ": orientasi paket harus terisi")
        copied.orientation = read_orientation({
            "w": orientation.w,
            "l": orientation.l,
            "h": orientation.h
        }, location + ".orientation")

        if original.position is not None:
            position = original.position
            copied.position = Position(
                read_integer(position.x, location + ".position.x"),
                read_integer(position.y, location + ".position.y"),
                read_integer(position.z, location + ".position.z")
            )

    return Problem(new_truck, new_packages)


def oriented_dim(package):
    dx, dy, dz = package.oriented_offset
    return abs(dx) + 1, abs(dy) + 1, abs(dz) + 1


def build_state(problem, max_cells=2_000_000):
    read_integer(max_cells, "max_cells", 1)
    copied_problem = copy_problem(problem)
    dimension = copied_problem.truck.dimension

    if dimension.w * dimension.l * dimension.h > max_cells:
        raise InputError("Jumlah sel grid melebihi batas max_cells")

    grid = []
    for z in range(dimension.h):
        layer = []
        for y in range(dimension.l):
            row = []
            for x in range(dimension.w):
                row.append(set())
            layer.append(row)
        grid.append(layer)

    for package in copied_problem.packages:
        if package.position is None:
            continue

        position = package.position
        dx, dy, dz = package.oriented_offset

        min_x = min(position.x, position.x + dx)
        max_x = max(position.x, position.x + dx)
        min_y = min(position.y, position.y + dy)
        max_y = max(position.y, position.y + dy)
        min_z = min(position.z, position.z + dz)
        max_z = max(position.z, position.z + dz)

        for z in range(max(0, min_z), min(dimension.h, max_z + 1)):
            for y in range(max(0, min_y), min(dimension.l, max_y + 1)):
                for x in range(max(0, min_x), min(dimension.w, max_x + 1)):
                    grid[z][y][x].add(package.id)

    return ProblemState(copied_problem, grid)
