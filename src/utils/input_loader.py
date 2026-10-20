import argparse
import json
from pathlib import Path

from ..models.dimension import Dimension
from ..models.package import Package, Position, Orientation
from ..models.problem import Problem
from ..models.truck import Truck


class InputError(ValueError):
    pass


def check_fields(data, required, optional, location):
    if not isinstance(data, dict):
        raise InputError(location + ": harus berupa object JSON")

    for field in required:
        if field not in data:
            raise InputError(location + ": field tidak ditemukan: " + field)

    for field in data:
        if field not in required and field not in optional:
            raise InputError(location + ": field tidak dikenal: " + field)


def read_integer(value, location, minimum=None):
    if type(value) is not int:
        raise InputError(location + ": harus berupa bilangan bulat")
    if minimum is not None and value < minimum:
        raise InputError(location + ": nilai minimum adalah " + str(minimum))
    return value


def read_dimension(data, location):
    check_fields(data, ("w", "l", "h"), (), location)
    w = read_integer(data["w"], location + ".w", 1)
    l = read_integer(data["l"], location + ".l", 1)
    h = read_integer(data["h"], location + ".h", 1)
    return Dimension(w, l, h)


def read_orientation(data, location):
    check_fields(data, ("w", "l", "h"), (), location)
    valid_axes = ("x", "y", "z", "-x", "-y", "-z")
    axes = []
    direction = 1

    for field in ("w", "l", "h"):
        axis = data[field]
        if axis not in valid_axes:
            raise InputError(location + "." + field + ": arah sumbu tidak valid")
        axes.append(axis[-1])
        if axis.startswith("-"):
            direction *= -1

    if len(set(axes)) != 3:
        raise InputError(location + ": setiap sisi harus menuju sumbu berbeda")

    axis_order = {"x": 0, "y": 1, "z": 2}
    for i in range(3):
        for j in range(i + 1, 3):
            if axis_order[axes[i]] > axis_order[axes[j]]:
                direction *= -1

    if direction != 1:
        raise InputError(location + ": orientasi merupakan pencerminan, bukan rotasi")

    return Orientation(data["w"], data["l"], data["h"])


def read_truck(data, location="truck"):
    check_fields(data, ("dimension", "max_capacity"), (), location)
    dimension = read_dimension(data["dimension"], location + ".dimension")
    capacity = read_integer(data["max_capacity"], location + ".max_capacity", 0)
    return Truck(dimension, capacity)


def read_trucks(data):
    if not isinstance(data, list):
        raise InputError("trucks: harus berupa array JSON")
    if len(data) == 0:
        raise InputError("trucks: minimal terdapat satu truk")

    trucks = []
    for index in range(len(data)):
        trucks.append(read_truck(data[index], "trucks[" + str(index) + "]"))
    return trucks


def read_packages(data):
    if not isinstance(data, list):
        raise InputError("packages: harus berupa array JSON")

    packages = []
    package_ids = set()
    required = ("id", "dimension", "value", "weight", "is_fragile", "eta")

    for index in range(len(data)):
        item = data[index]
        location = "packages[" + str(index) + "]"
        check_fields(item, required, (), location)

        package_id = item["id"]
        if not isinstance(package_id, str) or not package_id.strip():
            raise InputError(location + ".id: harus berupa teks yang tidak kosong")
        if package_id in package_ids:
            raise InputError(location + ".id: ID paket duplikat: " + package_id)
        package_ids.add(package_id)

        if type(item["is_fragile"]) is not bool:
            raise InputError(location + ".is_fragile: harus berupa boolean")

        package = Package(
            id=package_id,
            dimension=read_dimension(item["dimension"], location + ".dimension"),
            value=read_integer(item["value"], location + ".value", 0),
            weight=read_integer(item["weight"], location + ".weight", 1),
            is_fragile=item["is_fragile"],
            eta=read_integer(item["eta"], location + ".eta", 0)
        )
        packages.append(package)

    return packages


def read_truck_index(placement, trucks, location):
    # Format lama (satu truk) tidak memiliki field "truck", default ke truk 0.
    if "truck" not in placement:
        if len(trucks) == 1:
            return 0
        raise InputError(location + ".truck: wajib diisi jika truk lebih dari satu")

    index = read_integer(placement["truck"], location + ".truck", 0)
    if index >= len(trucks):
        raise InputError(location + ".truck: indeks truk tidak tersedia: " + str(index))
    return index


def read_placements(data, packages, trucks):
    package_ids = []
    for package in packages:
        package_ids.append(package.id)
    check_fields(data, package_ids, (), "initial_state")

    for package in packages:
        placement = data[package.id]
        if placement is None:
            continue

        location = "initial_state." + package.id
        check_fields(placement, ("position", "orientation"), ("truck",), location)
        position = placement["position"]
        check_fields(position, ("x", "y", "z"), (), location + ".position")

        package.position = Position(
            read_integer(position["x"], location + ".position.x"),
            read_integer(position["y"], location + ".position.y"),
            read_integer(position["z"], location + ".position.z")
        )
        package.orientation = read_orientation(
            placement["orientation"], location + ".orientation"
        )
        package.truck_idx = read_truck_index(placement, trucks, location)


def parse_problem(data):
    required = ("schema_version", "packages")
    check_fields(data, required, ("truck", "trucks", "initial_state"), "root")
    version = read_integer(data["schema_version"], "schema_version")
    if version != 1:
        raise InputError("schema_version: hanya versi 1 yang didukung")

    if "truck" in data and "trucks" in data:
        raise InputError("root: gunakan salah satu dari truck atau trucks")
    if "truck" in data:
        trucks = [read_truck(data["truck"])]
    elif "trucks" in data:
        trucks = read_trucks(data["trucks"])
    else:
        raise InputError("root: field tidak ditemukan: truck atau trucks")

    packages = read_packages(data["packages"])

    if "initial_state" in data:
        read_placements(data["initial_state"], packages, trucks)

    return Problem(trucks, packages)


def unique_fields(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("Field JSON duplikat: " + key)
        result[key] = value
    return result


def load_problem(path):
    try:
        with Path(path).open("r", encoding="utf-8-sig") as file:
            data = json.load(file, object_pairs_hook=unique_fields)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise InputError("Gagal membaca input: " + str(error)) from error
    return parse_problem(data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    args = parser.parse_args()

    try:
        problem = load_problem(args.input)
    except InputError as error:
        parser.exit(1, str(error) + "\n")

    print("Input berhasil dibaca.")
    print("Jumlah paket:", len(problem.packages))
    print("Jumlah truk:", len(problem.trucks))
    for index in range(len(problem.trucks)):
        truck = problem.trucks[index]
        print("Truk", index, "| dimensi:", truck.dimension, "| kapasitas berat:", truck.max_capacity)
    print("Konvensi koordinat: x=lebar, y=panjang, z=tinggi")

    for package in problem.packages:
        print(package.id, "| truk:", package.truck_idx, "| posisi:", package.position, "| orientasi:", package.orientation)

    print("Validitas susunan belum diperiksa; pemeriksaan dilakukan evaluator.")


if __name__ == "__main__":
    main()
