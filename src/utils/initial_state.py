from random import Random

from ..models.package import Position, Orientation
from .input_loader import InputError, read_orientation
from .state_builder import build_state, copy_problem


def create_rotations():
    axis_orders = [
        ("x", "y", "z"),
        ("x", "z", "y"),
        ("y", "x", "z"),
        ("y", "z", "x"),
        ("z", "x", "y"),
        ("z", "y", "x")
    ]
    rotations = []
    for axes in axis_orders:
        for width_sign in ("", "-"):
            for length_sign in ("", "-"):
                for height_sign in ("", "-"):
                    mapping = {
                        "w": width_sign + axes[0],
                        "l": length_sign + axes[1],
                        "h": height_sign + axes[2]
                    }
                    try:
                        orientation = read_orientation(mapping, "orientation")
                    except InputError:
                        continue
                    rotations.append(orientation)
    return rotations


ROTATIONS = create_rotations()


def dimensions_for_orientation(package, orientation):
    lengths = {}
    lengths[orientation.w[-1]] = package.dimension.w
    lengths[orientation.l[-1]] = package.dimension.l
    lengths[orientation.h[-1]] = package.dimension.h
    return lengths["x"], lengths["y"], lengths["z"]


def fitting_orientations(package, truck_dimension):
    choices = []
    for orientation in ROTATIONS:
        dx, dy, dz = dimensions_for_orientation(package, orientation)
        if dx <= truck_dimension.w and dy <= truck_dimension.l and dz <= truck_dimension.h:
            choices.append(orientation)
    return choices


def check_parameters(seed, load_probability):
    if seed is not None and type(seed) is not int:
        raise ValueError("Seed harus berupa bilangan bulat atau None")
    if type(load_probability) not in (int, float):
        raise ValueError("Load probability harus berupa angka antara 0 dan 1")
    if not 0 <= load_probability <= 1:
        raise ValueError("Load probability harus berada antara 0 dan 1")


def generate_initial_state(problem, seed=None, rng=None, load_probability=0.5):
    check_parameters(seed, load_probability)
    if seed is not None and rng is not None:
        raise ValueError("Gunakan seed atau rng, bukan keduanya")
    if rng is None:
        rng = Random(seed)

    candidate = copy_problem(problem)
    truck_dimension = candidate.truck.dimension

    for package in candidate.packages:
        package.position = None
        package.orientation = Orientation("x", "y", "z")

        if rng.random() >= load_probability:
            continue

        choices = fitting_orientations(package, truck_dimension)
        if not choices:
            continue

        selected = rng.choice(choices)
        package.orientation = Orientation(selected.w, selected.l, selected.h)
        dx, dy, dz = dimensions_for_orientation(package, package.orientation)

        x = rng.randint(0, truck_dimension.w - dx)
        y = rng.randint(0, truck_dimension.l - dy)
        z = rng.randint(0, truck_dimension.h - dz)

        offset_x, offset_y, offset_z = package.oriented_offset
        if offset_x < 0:
            x += abs(offset_x)
        if offset_y < 0:
            y += abs(offset_y)
        if offset_z < 0:
            z += abs(offset_z)

        package.position = Position(x, y, z)

    return build_state(candidate)


def generate_population(problem, population_size, seed=None, load_probability=0.5):
    if type(population_size) is not int or population_size < 1:
        raise ValueError("Population size harus berupa bilangan bulat positif")
    check_parameters(seed, load_probability)

    rng = Random(seed)
    population = []
    for index in range(population_size):
        state = generate_initial_state(
            problem,
            rng=rng,
            load_probability=load_probability
        )
        population.append(state)
    return population
