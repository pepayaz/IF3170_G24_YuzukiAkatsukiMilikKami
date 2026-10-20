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
    new_trucks = []
    for index in range(len(problem.trucks)):
        truck = problem.trucks[index]
        dimension = truck.dimension
        truck_data = {
            "dimension": {"w": dimension.w, "l": dimension.l, "h": dimension.h},
            "max_capacity": truck.max_capacity
        }
        new_trucks.append(read_truck(truck_data, "trucks[" + str(index) + "]"))

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
            truck_idx = read_integer(original.truck_idx, location + ".truck_idx", 0)
            if truck_idx >= len(new_trucks):
                raise InputError(location + ".truck_idx: indeks truk tidak tersedia: " + str(truck_idx))
            copied.truck_idx = truck_idx

    return Problem(new_trucks, new_packages)


def oriented_dim(package):
    dx, dy, dz = package.oriented_offset
    return abs(dx) + 1, abs(dy) + 1, abs(dz) + 1


def build_state(problem):
    copied_problem = copy_problem(problem)
    return ProblemState(copied_problem)
